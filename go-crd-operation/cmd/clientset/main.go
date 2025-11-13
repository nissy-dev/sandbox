package main

import (
	"context"
	"fmt"
	"path/filepath"

	examplev1 "github.com/nissy-dev/sandbox/go-crd-operation/pkg/apis/example.com/v1"
	clientset "github.com/nissy-dev/sandbox/go-crd-operation/pkg/generated/clientset/versioned"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

const namespace = "default"

func main() {
	ctx := context.Background()

	// クライアントの作成
	kubeconfigPath := filepath.Join(homedir.HomeDir(), ".kube", "config")
	cfg, _ := clientcmd.BuildConfigFromFlags("", kubeconfigPath)
	client, _ := clientset.NewForConfig(cfg)

	resourceClient := client.ExampleV1().MyResources(namespace)

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
		_, _ = resourceClient.Create(ctx, resource, metav1.CreateOptions{})
	}

	// リソース一覧を取得
	resourceList, _ := resourceClient.List(ctx, metav1.ListOptions{})
	for _, item := range resourceList.Items {
		fmt.Printf("  - Name: %s, Field1: %s, Field2: %d\n",
			item.Name, item.Spec.Field1, item.Spec.Field2)
	}

	// 作成したリソースを削除
	for _, name := range resourceNames {
		_ = resourceClient.Delete(ctx, name, metav1.DeleteOptions{})
	}
}
