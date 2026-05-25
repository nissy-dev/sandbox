# Test Sharding & Flaky Intelligence（仮）

- **ステータス**: 💡 アイデア
- **日付**: 2026-05-23
- **タグ**: CI, 開発者ツール, B2B SaaS, 個人開発

## 一言で

過去の実行時間ベースでテスト shard を賢く割り、flaky 解析もできる SaaS。**言語非依存**。各テストツールが出力する定番 JSON を ingest し、解釈・正規化は SaaS 側で行う。

## プロダクト像

```
CI（任意）→ 各ツールの JSON レポート → upload → SaaS
                                              ├─ 正規化（内部モデル）
                                              ├─ duration 履歴 → shard 提案
                                              └─ flaky ランキング
```

- **ユーザー向け独自 JSON スキーマは作らない**
- **ingest は各ツールの定番 JSON**（フラグ1つ / reporter 設定で出るもの）
- 内部で正規化モデルに落とし、sharding / flaky はそこから計算

## ざっくり機能（MVP 候補）

- [ ] CI からレポート upload（CLI or GitHub Action）
- [ ] 過去 run の duration 蓄積 → 次回 CI 用 **shard 割当 JSON**（matrix 向け）
- [ ] flaky 検出（同一 test ID の pass/fail 揺れ）
- [ ] ダッシュボード（遅いテスト Top N、flaky Top N）

Phase 2: GitHub App、複数 repo、チーム課金

## 拡張ガバナンス案との比較

| | 拡張 Private Marketplace | 本アイデア |
|--|-------------------------|-----------|
| 買い手 | 情シス | エンジニア / Platform |
| 販売 | 稟議・長いサイクル | PLG（GitHub Actions、クレカ） |
| 競合 | Admin, Open VSX | Launchable, Trunk, BuildPulse |
| トレンド | サプライチェーン攻撃 | CI 時間・flaky（常態） |

---

## 調査: 各ツールの JSON レポート

### 前提

- **「デフォルトで JSON が stdout に出る」ツールはほぼない**
- 実務では **定番の JSON 出力**（`-json` / `reporter: json` / プラグイン）を ingest 対象にする
- **Java は標準 JSON がなく例外** → JUnit XML アダプタを別途

### 一覧

| ツール | デフォルト出力 | JSON の出し方 | 安定性 | 形式 |
|--------|----------------|---------------|--------|------|
| **Go** | テキスト | `go test -json ./...` | ◎ 標準・安定 | **NDJSON**（`TestEvent` 1行1件） |
| **gotestsum** | — | `--jsonfile` / `--junitfile` | ◎ | `go test -json` 同系統 or JUnit |
| **Vitest** | ターミナル | `reporters: [['json', { outputFile }]]` | ◎ | Jest 互換・**1 JSON ファイル** |
| **Jest** | ターミナル | `--json --outputFile=...` | ◎ | Vitest と同型 |
| **Playwright** | `list` 等 | `reporter: [['json', { outputFile }]]` | ◎ | suite/spec **ツリー型** 1 JSON |
| **pytest** | テキスト | **`pytest-json-report`** プラグイン | ◎ de facto | 1 JSON（**標準機能ではない**） |
| **Rust `cargo test`** | テキスト | `-Z unstable-options --format json` | △ 不安定 | libtest JSON（nightly 寄り） |
| **cargo-nextest** | 人間向け | `--message-format libtest-json` | △ **実験的** | libtest JSON エミュ |
| **nextest** | — | JUnit XML（設定で安定） | ◎ | XML（JSON より先に対応しても可） |
| **Java Surefire** | **JUnit XML** | 標準 JSON なし | — | `TEST-*.xml` |

### Go: `go test -json`

- 公式: [Go test2json / TestEvent](https://pkg.go.dev/cmd/test2json)
- **NDJSON**（newline-delimited）。単一 JSON ファイルではない

```bash
go test -json ./... > report.ndjson
```

主要フィールド:

```json
{"Time":"...","Action":"pass","Package":"pkg/foo","Test":"TestBar","Elapsed":0.04}
```

- `Action`: `run`, `pass`, `fail`, `skip`, `output`, ...
- sharding: `Package` + `Test` を `test_id` に。ファイルパスは間接的
- ingest: **行ごとパース → イベントをテスト単位に集約**

### Vitest / Jest JSON

- Vitest: [Reporters - JSON](https://vitest.dev/guide/reporters.html)
- Jest 互換の `--json` 出力

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    reporters: [['json', { outputFile: 'report.json' }]],
  },
})
```

主要構造:

- トップ: `numTotalTests`, `testResults[]`
- 各ファイル: `testResults[].name`（ファイルパス）, `assertionResults[]`
- 各テスト: `fullName`, `status`, `duration`, `location.line/column`

→ **ファイルパス + duration が取りやすく sharding に最適**

### Playwright JSON

- [Reporters - JSON](https://playwright.dev/docs/test-reporters)

```bash
PLAYWRIGHT_JSON_OUTPUT_NAME=results.json npx playwright test --reporter=json
```

```ts
reporter: [['json', { outputFile: 'results.json' }]],
```

- suite / spec / test のツリー
- `file`, `line`, `column`, 各 test の `status`, `duration`
- retry 設定と相性が良い（flaky 向き）

### pytest

- **標準では JSON なし**（デフォルトは JUnit XML: `--junitxml`）
- 定番: [pytest-json-report](https://github.com/numirias/pytest-json-report)

```bash
pytest --json-report --json-report-file=report.json
```

- デフォルト保存先: `.report.json`
- `tests[]` に `nodeid`, `duration`, `outcome` 等
- 本体の `report.to_json()` / `from_json()`（xdist 由来）もあるが、ファイル出力はプラグインが de facto

### Rust

**cargo test**

```bash
RUSTC_BOOTSTRAP=1 cargo test -- -Z unstable-options --format json --report-time
```

- 不安定。本番 ingest は後回しでも可

**cargo-nextest**

- JUnit: [nextest JUnit](https://nexte.st/docs/machine-readable/junit/) — **安定・推奨（XML）**
- JSON: [libtest JSON](https://nexte.st/docs/machine-readable/libtest-json/) — `NEXTEST_EXPERIMENTAL_LIBTEST_JSON=1` + `--message-format libtest-json`
- 追跡: [nextest #1152](https://github.com/nextest-rs/nextest/issues/1152)

```bash
NEXTEST_EXPERIMENTAL_LIBTEST_JSON=1 cargo nextest run --message-format libtest-json
```

### Java

- Surefire / Gradle: デフォルト **`target/surefire-reports/TEST-*.xml`**
- 標準 JSON レポーターはない
- 対応案: **JUnit XML アダプタ** を ingest の例外として1本持つ

---

## 調査: JUnit XML との比較

以前は JUnit XML を横断フォーマットとして検討した。

| | JUnit XML | 各ツールの定番 JSON |
|--|-----------|---------------------|
| 横断性 | ◎ 多くのツールが出せる | △ Java は XML、他は JSON |
| duration / path | △ ツール依存 | ◎ Vitest/Playwright は豊富 |
| 実装 | 1パーサーで済む | **ツール別 adapter** が必要 |
| ユーザー設定 | 多くは標準で XML | JSON は reporter 設定が必要 |

**結論（2026-05-23）**: ingest の主軸は **定番 JSON + adapter**。Java のみ **JUnit XML adapter** で補完。

---

## 調査: アーキテクチャ（Adapter パターン）

```
upload (report.json | report.ndjson | TEST-*.xml)
        │
        ├─ detect format (auto / --format)
        │
        ├─ parser: vitest-jest-json
        ├─ parser: playwright-json
        ├─ parser: go-test-ndjson
        ├─ parser: pytest-json-report
        ├─ parser: nextest-junit-xml   # 任意
        └─ parser: surefire-junit-xml  # Java
        │
        ▼
   Canonical TestRun（内部のみ）
        │
        ├─ test_id (安定キー)
        ├─ file_path | package | suite
        ├─ status, duration_ms
        └─ run metadata (commit, branch, shard_index, ...)
        │
        ▼
   sharding engine / flaky engine
```

### 内部正規化モデル（案）

| フィールド | 用途 |
|------------|------|
| `test_id` | 履歴のキー（言語横断） |
| `file_path` | shard 単位（ファイル分割） |
| `duration_ms` | bin packing |
| `status` | pass / fail / skip |
| `run_id`, `commit`, `branch` | CI コンテキスト |
| `shard_index`, `shard_total` | 今回 run の割当（任意） |

### test_id の付け方（例）

| ソース | test_id 例 |
|--------|------------|
| Vitest | `{file}::{fullName}` |
| Playwright | `{file}::{title}` |
| Go | `{package}::{Test}` |
| pytest | `{nodeid}` |

---

## 調査: sharding / flaky に使えるフィールド

| ソース | duration | file path | retry / flaky ヒント |
|--------|----------|-----------|----------------------|
| Go `-json` | ◎ `Elapsed` | △ package | △ イベント列 |
| Vitest/Jest | ◎ | ◎ `testResults[].name` | △ |
| Playwright | ◎ | ◎ | ◎ retry 設定 |
| pytest-json-report | ◎ | ◎ `nodeid` | △ |
| JUnit XML | △ | △ classname | △ nextest の flaky 拡張 |

**flaky 定義（案）**: 同一 `test_id` が直近 N run で pass/fail が混在（同一 commit 除外オプションあり）。

---

## MVP: ingest パーサー優先順位

1. **Vitest / Jest JSON** — 1ファイル、ドキュメント豊富
2. **Playwright JSON** — E2E 需要
3. **Go `test -json`（NDJSON）** — バックエンド系
4. **pytest-json-report**
5. **JUnit XML**（Java / nextest）— 例外アダプタ

Rust native JSON（libtest）は **実験的なので Phase 2 以降**。

---

## ユーザー向けドキュメント例

```yaml
# vitest.config.ts
test:
  reporters: [['json', { outputFile: 'report.json' }]]
```

```yaml
# playwright.config.ts
reporter: [['json', { outputFile: 'report.json' }]]
```

```bash
# Go
go test -json ./... > report.ndjson

# pytest
pytest --json-report --json-report-file=report.json

# upload
testintel upload report.json    # format auto-detect
testintel upload report.ndjson
```

---

## 競合・参考

| プロダクト | 強み | 本アイデアとの差 |
|-----------|------|------------------|
| [Launchable](https://www.launchableinc.com/) | テスト選択・優先 | 軽量・shard 特化・安価 |
| Trunk / BuildPulse | flaky 検知 | ingest を既存 JSON ベースに |
| CircleCI test splitting | 時間ベース split | **CI 非依存** |
| gotestsum | Go の JUnit/JSON | マルチ言語 + SaaS 履歴 |

---

## 懸念・未解決

- 初回は履歴がなく shard 提案の精度が低い → round-robin フォールバック
- NDJSON（Go）と 1ファイル JSON で ingest API を分けるか
- pytest はプラグイン必須 → 「標準に近い」表現の仕方
- プライバシー: 失敗メッセージに secrets が含まれる → upload 時に omit オプション

## メモ

- 名前案: `shardwise`, `testsplit`, `flakyboard`
- CLI + GitHub Action から検証しやすい
- 拡張 Marketplace 案は [別ファイル](./2026-05-23-private-tool-marketplace.md)

## 参考リンク

- [go test -json proposal](https://go.googlesource.com/proposal/+/master/design/2981-go-test-json.md)
- [cmd/test2json - TestEvent](https://pkg.go.dev/cmd/test2json)
- [Vitest Reporters](https://vitest.dev/guide/reporters)
- [Playwright Reporters](https://playwright.dev/docs/test-reporters)
- [pytest-json-report](https://github.com/numirias/pytest-json-report)
- [cargo-nextest JUnit](https://nexte.st/docs/machine-readable/junit/)
- [cargo-nextest libtest JSON](https://nexte.st/docs/machine-readable/libtest-json/)
- [Maven Surefire reports](https://maven.apache.org/surefire/maven-surefire-plugin/)
