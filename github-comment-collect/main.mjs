import { Octokit } from "@octokit/rest";
import fs from "fs/promises";

// 環境変数から設定を取得
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = process.env.REPO_OWNER || "biomejs";
const REPO_NAME = process.env.REPO_NAME || "biome";
const USERNAME = process.env.GITHUB_USERNAME || "nissy-dev"; // 自分のGitHubユーザー名

// 無視したいユーザーのリスト
const IGNORED_USERS = [
  USERNAME, // 自分のコメント
  "github-actions[bot]",
  "dependabot[bot]",
  "renovate[bot]",
  // 他にも無視したいユーザーがあれば追加
  "Copilot",
];

if (!GITHUB_TOKEN) {
  console.error("Error: GITHUB_TOKEN environment variable is required");
  process.exit(1);
}

const octokit = new Octokit({ auth: GITHUB_TOKEN });

// コメント/レビューをフィルタリングする共通関数
function filterComments(items) {
  return items.filter((item) => !IGNORED_USERS.includes(item.user.login));
}

async function getMyPullRequests() {
  console.log(`Fetching PRs for ${REPO_OWNER}/${REPO_NAME}...`);

  let allPullRequests = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const query = `is:pr repo:${REPO_OWNER}/${REPO_NAME} author:${USERNAME}`;
    const res = await octokit.rest.search.issuesAndPullRequests({
      q: query,
      per_page: 100,
      page,
    });
    const pullRequests = res.data.items;
    allPullRequests = allPullRequests.concat(pullRequests);
    console.log(`Fetched page ${page}: ${pullRequests.length} PRs`);

    if (pullRequests.length < 100) {
      hasMore = false;
    } else {
      page++;
    }
  }

  console.log(`Total PRs fetched: ${allPullRequests.length}`);
  return allPullRequests;
}

async function getReviewComments(prNumber) {
  console.log(`Fetching review comments for PR #${prNumber}...`);

  const { data: reviewComments } = await octokit.pulls.listReviewComments({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    pull_number: prNumber,
    per_page: 100,
  });

  return filterComments(reviewComments);
}

// async function getReviews(prNumber) {
//   console.log(`Fetching reviews for PR #${prNumber}...`);

//   const { data: reviews } = await octokit.pulls.listReviews({
//     owner: REPO_OWNER,
//     repo: REPO_NAME,
//     pull_number: prNumber,
//     per_page: 100,
//   });

//   return filterComments(reviews);
// }

async function getIssueComments(prNumber) {
  console.log(`Fetching issue comments for PR #${prNumber}...`);

  const { data: comments } = await octokit.issues.listComments({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    issue_number: prNumber,
    per_page: 100,
  });

  return filterComments(comments);
}

function generateMarkdown(prs, prComments) {
  let markdown = `# Pull Request Review Comments\n\n`;
  markdown += `Repository: ${REPO_OWNER}/${REPO_NAME}\n`;
  markdown += `User: ${USERNAME}\n`;
  markdown += `Generated: ${new Date().toISOString()}\n\n`;
  markdown += `---\n\n`;

  for (const pr of prs) {
    const comments = prComments[pr.number];

    markdown += `## PR #${pr.number}: ${pr.title}\n\n`;
    markdown += `**URL**: ${pr.html_url}\n`;
    markdown += `**State**: ${pr.state}\n`;
    markdown += `**Created**: ${pr.created_at}\n`;
    markdown += `**Updated**: ${pr.updated_at}\n\n`;

    // Review comments (コードに対するコメント)
    if (comments.reviewComments.length > 0) {
      markdown += `### Review Comments (${comments.reviewComments.length})\n\n`;
      for (const comment of comments.reviewComments) {
        markdown += `#### ${comment.user.login} - ${comment.created_at}\n`;
        markdown += `**File**: \`${comment.path}\`\n`;
        if (comment.line) {
          markdown += `**Line**: ${comment.line}\n`;
        }
        markdown += `\n${comment.body}\n\n`;

        if (comment.diff_hunk) {
          markdown += `<details>\n<summary>Code Context</summary>\n\n\`\`\`diff\n${comment.diff_hunk}\n\`\`\`\n\n</details>\n\n`;
        }

        markdown += `---\n\n`;
      }
    }

    // // Reviews (Approve, Request Changes, Comment)
    // if (comments.reviews.length > 0) {
    //   markdown += `### Reviews (${comments.reviews.length})\n\n`;
    //   for (const review of comments.reviews) {
    //     if (review)
    //     markdown += `#### ${review.user.login} - ${review.state} - ${review.submitted_at}\n`;
    //     if (review.body) {
    //       markdown += `\n${review.body}\n`;
    //     }
    //     markdown += `\n---\n\n`;
    //   }
    // }

    // Issue comments (PRの会話コメント)
    if (comments.issueComments.length > 0) {
      markdown += `### General Comments (${comments.issueComments.length})\n\n`;
      for (const comment of comments.issueComments) {
        markdown += `#### ${comment.user.login} - ${comment.created_at}\n`;
        markdown += `\n${comment.body}\n\n`;
        markdown += `---\n\n`;
      }
    }

    markdown += `\n\n`;
  }

  return markdown;
}

async function main() {
  try {
    // 自分のPRを取得
    const myPRs = await getMyPullRequests();
    console.log(`Found ${myPRs.length} PRs created by ${USERNAME}`);

    if (myPRs.length === 0) {
      console.log("No PRs found. Exiting...");
      return;
    }

    // 各PRのコメントを取得
    const prComments = {};
    for (const pr of myPRs) {
      const [reviewComments, reviews, issueComments] = await Promise.all([
        getReviewComments(pr.number),
        // getReviews(pr.number),
        getIssueComments(pr.number),
      ]);

      prComments[pr.number] = {
        reviewComments,
        // reviews,
        issueComments,
      };
    }

    // Markdownを生成
    const markdown = generateMarkdown(myPRs, prComments);

    // ファイルに書き出し
    const filename = `pr-comments-${REPO_NAME}-${Date.now()}.md`;
    await fs.writeFile(filename, markdown, "utf-8");

    console.log(`\nSuccessfully written to ${filename}`);
    console.log(`Total PRs: ${myPRs.length}`);
  } catch (error) {
    console.error("Error:", error.message);
    process.exit(1);
  }
}

main();
