package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"time"

	examplev1 "github.com/nissy-dev/sandbox/go-crd-operation/pkg/apis/example.com/v1"
	clientset "github.com/nissy-dev/sandbox/go-crd-operation/pkg/generated/clientset/versioned"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

const namespace = "default"

func main() {
	var kubeconfigPath *string
	if home := homedir.HomeDir(); home != "" {
		kubeconfigPath = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "kubeconfig file path")
	} else {
		kubeconfigPath = flag.String("kubeconfig", "", "kubeconfig file path")
	}
	flag.Parse()

	// クライアントの作成
	cfg, err := clientcmd.BuildConfigFromFlags("", *kubeconfigPath)
	if err != nil {
		fmt.Printf("Error building config: %v\n", err)
		os.Exit(1)
	}

	client, err := clientset.NewForConfig(cfg)
	if err != nil {
		fmt.Printf("Error creating clientset: %v\n", err)
		os.Exit(1)
	}

	ctx := context.Background()

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

		_, err := client.ExampleV1().MyResources(namespace).Create(ctx, resource, metav1.CreateOptions{})
		if err != nil {
			continue
		}
	}

	// リソース一覧を取得
	time.Sleep(2 * time.Second)

	resourceList, err := client.ExampleV1().MyResources(namespace).List(ctx, metav1.ListOptions{})
	if err != nil {
		os.Exit(1)
	}
	for _, item := range resourceList.Items {
		fmt.Printf("  - Name: %s, Field1: %s, Field2: %d\n",
			item.Name, item.Spec.Field1, item.Spec.Field2)
	}

	// 作成したリソースを削除
	time.Sleep(2 * time.Second)

	for _, name := range resourceNames {
		err := client.ExampleV1().MyResources(namespace).Delete(ctx, name, metav1.DeleteOptions{})
		if err != nil {
			continue
		}
	}
}
