# Private Extension Platform（仮）

- **ステータス**: 💡 アイデア
- **日付**: 2026-05-23
- **タグ**: 情シス, B2B SaaS, エンタープライズ, DevTools

## 一言で

Cloudflare のような SaaS で、情シスが Chrome 拡張・VS Code 拡張を **登録・承認・ポリシー化** できる Private Marketplace。実際の端末への配布は情シスが既存手段（Intune, Google Admin, GPO 等）で行う前提。

## スコープ

| SaaS がやる | 情シスがやる（本プロダクトの外） |
|-------------|----------------------------------|
| カタログ・レジストリ | 端末への install / force-install |
| 承認ワークフロー | Intune / Google Admin / GPO 等での適用 |
| Allowlist / Blocklist の定義 | 社内ネットワーク・MDM への反映 |
| アーティファクトホスティング（CRX / VSIX） | 入社・退社時の端末オペレーション |
| 監査ログ・ポリシー変更履歴 | Google アカウント有無など環境差の吸収 |

**配布は情シスがいい感じにやる** — Agent 開発や MDM コネクタは作らない。SaaS は **コントロールプレーン + カタログ** に集中する。

## プロダクト像

**買い手は情シス。利用者は社員。作者は社内開発チーム。**

```
┌─────────────────────────────────────────────────────────┐
│  Private Extension Platform（SaaS）                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐  │
│  │ カタログ │ │ 承認    │ │ ポリシー │ │ 監査ログ     │  │
│  └─────────┘ └─────────┘ └─────────┘ └──────────────┘  │
│  ┌─────────────────────────────────────────────────┐    │
│  │  アーティファクト置き場（CRX / VSIX）            │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────┘
                           │ ダウンロード URL / ポリシー export
                           ▼
              情シス（Intune, Admin Console, GPO, 手動…）
                           ▼
              社員の Chrome / VS Code
```

Google アカウントの有無、MDM の種類、オンプレ AD かクラウド IdP か — こうした環境差は **全部情シス側の配布オペレーション** に任せる。SaaS は Google 必須にしない。

## 背景・きっかけ

情シスが抱える典型パターン:

- 社内作拡張が Slack や共有ドライブに散らばり、正規版が分からない
- 公開ストアに出せない拡張の **置き場と承認フロー** がない
- Allowlist を Excel で管理している
- VS Code 拡張を載せたいが Open VSX の self-host 運用が重い
- 「いつ誰が承認して、どのバージョンが正か」が監査で説明できない

## 解決したい課題

| 誰 | 課題 |
|----|------|
| **情シス** | 拡張の一覧・承認状態・バージョンが一元管理できていない |
| **情シス** | 配布用 URL や manifest ID を毎回探し直している |
| **情シス** | 監査対応で「何を許可しているか」を残したい |
| **社内開発** | 情シスに出す申請フォーマットが拡張ごとにバラバラ |
| **社員** | 社内で使っていい拡張がどれか分からない |

## ざっくり機能

### 管理コンソール（情シス向け）

- [ ] 組織（テナント）・グループ単位のポリシー定義
- [ ] **Allowlist / Blocklist**
- [ ] **必須拡張リスト**（Force install 対象の定義。適用は情シスが MDM 等で）
- [ ] 申請ワークフロー（開発チーム提出 → 情シス承認 → カタログ公開）
- [ ] 監査ログ（承認・公開・ポリシー変更）
- [ ] 情シス向け SSO（Entra ID / Okta / Google Workspace いずれも可）

### カタログ・レジストリ

- [ ] 社内登録拡張の一覧（Chrome / VS Code）
- [ ] 公開ストア拡張の「社内承認済み」マーキング
- [ ] バージョン履歴・リリースノート
- [ ] 拡張メタデータ（説明、権限、所有者、レビュー状態）
- [ ] **配布用情報の提示**: 拡張 ID、ダウンロード URL、Intune / Admin Console 用の設定値

### アーティファクトホスティング

- [ ] `.crx` / `.vsix` のホスティング（署名済み URL）
- [ ] 情シスは S3 や社内ファイルサーバを自前で立てなくてよい

### 開発チーム向け（サブ UI）

- [ ] 拡張の登録申請（manifest / vsix アップロード）
- [ ] 権限一覧の自動抽出
- [ ] 承認ステータスの確認

### 情シス向け export（配布の手助け程度）

- [ ] ポリシーを CSV / JSON で export
- [ ] Chrome `ExtensionInstallForcelist` 用の値一覧
- [ ] 配布手順テンプレ（Intune / Google Admin 向けドキュメント生成）

※ 自動 sync や Agent は **スコープ外**。

## Cloudflare との対応イメージ

| Cloudflare | 本プロダクト |
|------------|-------------|
| DNS レコード管理 | 拡張カタログ・メタデータ管理 |
| Firewall Rule 定義 | Allow / Block ポリシー定義 |
| Analytics / Logs | 承認・公開の監査ログ |
| 設定 UI | 情シス向け管理コンソール |
| 実際のトラフィック処理 | **情シスの配布オペレーション**（Cloudflare エッジに相当する部分は顧客側） |

## 技術・スタック案

- **SaaS マルチテナント**: PostgreSQL + RLS
- **管理 UI**: Next.js
- **Artifact Store**: Cloudflare R2 + CDN
- **認証**: 情シス・開発者向け SSO
- **Gallery API**（任意）: VS Code private marketplace 互換 endpoint — IDE がここを向けばユーザー自身で install も可能（配布の補助）

## 既存の似たもの

| プロダクト | 足りない点 |
|-----------|-----------|
| Open VSX self-hosted | 情シス向け SaaS ではない、承認フロー・横断カタログなし |
| Google Admin | Chrome のみ、カタログ・承認の横断管理なし |
| 社内 Wiki + 共有ドライブ | バージョン管理・監査・ポリシーが効かない |

→ **拡張特化の private marketplace + ガバナンス** が価値。配布実行は情シスの既存ツールに乗せる。

## ビジネスモデル案

- テナント数 × 登録拡張数 or 席課金
- Enterprise: SSO, 監査ログ長期保存, 専任サポート

## 懸念・未解決

- 「ポリシーを定義するだけ」だと情シスにとって価値が弱く見えない — export と手順テンプレで配布の手間を減らす必要
- VS Code private gallery を提供するか、ホスティング + URL 渡しだけにするか
- 公開ストア拡張の Allowlist をどこまで自動でメタデータ取得するか

## MVP 案

1. カタログ + CRX / VSIX ホスティング
2. 申請 → 承認ワークフロー
3. Allowlist 定義 + Chrome force-install 用 ID 一覧 export
4. 監査ログ

配布コネクタ・Agent は作らない。パイロット顧客の情シスと一緒に「export した値を Intune に入れる」オペレーションを確認する。

## 参考リンク

- [VS Code - Private Extension Marketplace](https://code.visualstudio.com/docs/setup/enterprise#_private-marketplace)
- [Chrome Enterprise - Manage extensions](https://support.google.com/chrome/a/answer/9296680)
- [Open VSX Wiki - Deploying Open VSX](https://github.com/EclipseFdn/open-vsx.org/wiki/Deploying-Open-VSX)

## メモ

- 名前案: `extguard`, `policyforge`, `innerext`
- セールス: 「拡張の App Store Connect」— 審査・公開・バージョン管理。配布はお客様の MDM で
- Google なし環境も問題なし（SaaS 側は Google 非依存。配布は情シスが Intune / 手動等で対応）
