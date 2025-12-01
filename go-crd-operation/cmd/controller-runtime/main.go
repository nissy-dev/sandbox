package main

import (
	"context"
	"fmt"
	"path/filepath"

	examplev1 "github.com/nissy-dev/sandbox/go-crd-operation/pkg/apis/example.com/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

const namespace = "default"

var SchemeGroupVersion = schema.GroupVersion{
	Group:   "example.com",
	Version: "v1",
}

func addKnownTypes(scheme *runtime.Scheme) error {
	scheme.AddKnownTypes(
		SchemeGroupVersion,
		&examplev1.MyResource{},
		&examplev1.MyResourceList{},
	)
	metav1.AddToGroupVersion(scheme, SchemeGroupVersion)
	return nil
}

func main() {
	ctx := context.Background()

	// Scheme の作成（型を登録）
	scheme := runtime.NewScheme()
	schemeBuilder := runtime.NewSchemeBuilder(addKnownTypes)
	schemeBuilder.AddToScheme(scheme)

	// controller-runtime clientの作成
	kubeconfigPath := filepath.Join(homedir.HomeDir(), ".kube", "config")
	cfg, _ := clientcmd.BuildConfigFromFlags("", kubeconfigPath)
	k8sClient, _ := client.New(cfg, client.Options{Scheme: scheme})

	// カスタムリソースを複数作成
	resourceNames := []string{"sample-resource-1", "sample-resource-2", "sample-resource-3"}
	for i, name := range resourceNames {
		resource := &examplev1.MyResource{
			ObjectMeta: metav1.ObjectMeta{
				Name:      name,
				Namespace: namespace,
			},
			Spec: examplev1.MyResourceSpec{
				Field1: fmt.Sprintf("value-%d", i+1),
				Field2: int32((i + 1) * 100),
			},
		}
		_ = k8sClient.Create(ctx, resource)
	}

	// リソース一覧を取得
	resourceList := &examplev1.MyResourceList{}
	_ = k8sClient.List(ctx, resourceList)
	for _, item := range resourceList.Items {
		fmt.Printf("  - Name: %s, Field1: %s, Field2: %d\n",
			item.Name, item.Spec.Field1, item.Spec.Field2)
	}

	// 作成したリソースを削除
	for _, name := range resourceNames {
		resource := &examplev1.MyResource{
			ObjectMeta: metav1.ObjectMeta{
				Name:      name,
				Namespace: namespace,
			},
		}
		_ = k8sClient.Delete(ctx, resource)
	}
}
