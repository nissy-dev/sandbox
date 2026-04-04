# pnpm ignore-scripts / 依存 postinstall ラボ

## ケース別の結果（観測）

| ケースディレクトリ | 主な設定 | postinstall は実行されるか | 補足 |
|-------------------|----------|---------------------------|------|
| [`cases/case-default-no-config/`](cases/case-default-no-config/) | ビルド／スクリプト系の追加設定なし | **いいえ** | v10 のデフォルトで `test` のスクリプトは許可されない |
| [`cases/case-npmrc-ignore-scripts/`](cases/case-npmrc-ignore-scripts/) | `.npmrc` で `ignore-scripts=false`。` | **いいえ** | `ignore-scripts=false` 単体では依存の postinstall は走らない。 |
| [`cases/case-only-built-allows-test/`](cases/case-only-built-allows-test/) | `ignoreScripts: false` と `onlyBuiltDependencies: []`（`test` は含めない） | **いいえ** | リストに無いパッケージのスクリプトは実行されない |
| [`cases/case-only-built-includes-test/`](cases/case-only-built-includes-test/) | `onlyBuiltDependencies: [test]`。`ignoreScripts` は未指定 | **はい** | 許可リストに `test` があれば postinstall が走る |
| [`cases/case-only-built-includes-test-ignore-dep-scripts-false/`](cases/case-only-built-includes-test-ignore-dep-scripts-false/) | 上に加え `ignoreScripts: false` を明示 | **はい** | 上記と同様に実行される（本リポジトリでは差は出ていない） |

## CI

手動実行: **Actions → "pnpm ignore-scripts lab" → Run workflow**。