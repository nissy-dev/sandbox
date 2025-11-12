package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"time"

	examplev1 "github.com/nissy-dev/sandbox/go-crd-operation/pkg/apis/example.com/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
	"sigs.k8s.io/controller-runtime/pkg/client"
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

	// Schemeの作成
	scheme := runtime.NewScheme()
	if err := examplev1.Install(scheme); err != nil {
		fmt.Printf("Error adding to scheme: %v\n", err)
		os.Exit(1)
	}

	// controller-runtime clientの作成
	cfg, err := clientcmd.BuildConfigFromFlags("", *kubeconfigPath)
	if err != nil {
		fmt.Printf("Error building config: %v\n", err)
		os.Exit(1)
	}

	k8sClient, err := client.New(cfg, client.Options{Scheme: scheme})
	if err != nil {
		fmt.Printf("Error creating client: %v\n", err)
		os.Exit(1)
	}

	ctx := context.Background()

	// カスタムリソースを複数作成
	fmt.Println("Creating MyResources...")
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

		if err := k8sClient.Create(ctx, resource); err != nil {
			fmt.Printf("Failed to create %s: %v\n", name, err)
			continue
		}
		fmt.Printf("Created: %s\n", resource.Name)
	}

	// リソース一覧を取得
	time.Sleep(2 * time.Second)
	fmt.Println("\nListing MyResources...")

	resourceList := &examplev1.MyResourceList{}
	if err := k8sClient.List(ctx, resourceList, client.InNamespace(namespace)); err != nil {
		fmt.Printf("Error listing resources: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Found %d resources:\n", len(resourceList.Items))
	for _, item := range resourceList.Items {
		fmt.Printf("  - Name: %s, Field1: %s, Field2: %d\n",
			item.Name, item.Spec.Field1, item.Spec.Field2)
	}

	// 作成したリソースを削除
	time.Sleep(2 * time.Second)
	fmt.Println("\nDeleting MyResources...")

	for _, name := range resourceNames {
		resource := &examplev1.MyResource{
			ObjectMeta: metav1.ObjectMeta{
				Name:      name,
				Namespace: namespace,
			},
		}
		if err := k8sClient.Delete(ctx, resource); err != nil {
			fmt.Printf("Failed to delete %s: %v\n", name, err)
			continue
		}
		fmt.Printf("Deleted: %s\n", name)
	}

	fmt.Println("\nCompleted!")
}
