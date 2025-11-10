// カスタムリソースの構造体定義を行う
// metav1.TypeMeta を保持するトップレベル型には、特別な deepcopy-gen タグが必要になる

package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// +genclient
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// MyResource is a specification for a MyResource resource
type MyResource struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   MyResourceSpec   `json:"spec"`
	Status MyResourceStatus `json:"status,omitempty"`
}

// MyResourceSpec is the spec for a MyResource resource
type MyResourceSpec struct {
	Field1 string `json:"field1"`
	Field2 int32  `json:"field2"`
}

// MyResourceStatus is the status for a MyResource resource
type MyResourceStatus struct {
	State string `json:"state,omitempty"`
}

// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

// MyResourceList is a list of MyResource resources
type MyResourceList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata"`

	Items []MyResource `json:"items"`
}
