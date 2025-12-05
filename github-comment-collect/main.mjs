import { Octokit } from "@octokit/rest";
import fs from "fs/promises";

// 環境変数から設定を取得
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = process.env.REPO_OWNER || "biomejs";
const REPO_NAME = process.env.REPO_NAME || "biome";
const USERNAME = process.env.GITHUB_USERNAME || "nissy-dev"; // 自分のGitHubユーザー名

if (!GITHUB_TOKEN) {
  console.error("Error: GITHUB_TOKEN environment variable is required");
  process.exit(1);
}

const octokit = new Octokit({ auth: GITHUB_TOKEN });

async function getMyPullRequests() {
  console.log(`Fetching PRs for ${REPO_OWNER}/${REPO_NAME}...`);

  let allPullRequests = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const { data: pullRequests } = await octokit.pulls.list({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      state: "closed",
      head: `user:${USERNAME}`,
      per_page: 100,
      page,
    });

    allPullRequests = allPullRequests.concat(pullRequests);
    console.log(`Fetched page ${page}: ${pullRequests.length} PRs`);

    if (pullRequests.length < 100) {
      hasMore = false;
    } else {
      page++;
    }
  }

  console.log(`Total PRs fetched: ${allPullRequests.length}`);

  console.log(allPullRequests);

  // 自分が作成したPRのみをフィルタ
  return allPullRequests.filter((pr) => pr.user.login === USERNAME);
}

async function getReviewComments(prNumber) {
  console.log(`Fetching review comments for PR #${prNumber}...`);

  const { data: reviewComments } = await octokit.pulls.listReviewComments({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    pull_number: prNumber,
    per_page: 100,
  });

  // 自分のコメントを除外
  return reviewComments.filter((comment) => comment.user.login !== USERNAME);
}

async function getReviews(prNumber) {
  console.log(`Fetching reviews for PR #${prNumber}...`);

  const { data: reviews } = await octokit.pulls.listReviews({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    pull_number: prNumber,
    per_page: 100,
  });

  // 自分のレビューを除外
  return reviews.filter((review) => review.user.login !== USERNAME);
}

async function getIssueComments(prNumber) {
  console.log(`Fetching issue comments for PR #${prNumber}...`);

  const { data: comments } = await octokit.issues.listComments({
    owner: REPO_OWNER,
    repo: REPO_NAME,
    issue_number: prNumber,
    per_page: 100,
  });

  // 自分のコメントを除外
  return comments.filter((comment) => comment.user.login !== USERNAME);
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

    if (pr.body) {
      markdown += `### Description\n\n${pr.body}\n\n`;
    }

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

    // Reviews (Approve, Request Changes, Comment)
    if (comments.reviews.length > 0) {
      markdown += `### Reviews (${comments.reviews.length})\n\n`;
      for (const review of comments.reviews) {
        markdown += `#### ${review.user.login} - ${review.state} - ${review.submitted_at}\n`;
        if (review.body) {
          markdown += `\n${review.body}\n`;
        }
        markdown += `\n---\n\n`;
      }
    }

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
        getReviews(pr.number),
        getIssueComments(pr.number),
      ]);

      prComments[pr.number] = {
        reviewComments,
        reviews,
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
