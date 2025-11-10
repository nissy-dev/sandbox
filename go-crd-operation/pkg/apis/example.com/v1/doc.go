// doc.go ではグローバルのタグの定義を行う
// deepcopy の有効化とAPI グループの設定

// +k8s:deepcopy-gen=package
// +groupName=example.com
package v1
