package main

import (
	"context"
	"fmt"
	"path/filepath"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

const namespace = "default"

var myResourceGVR = schema.GroupVersionResource{
	Group:    "example.com",
	Version:  "v1",
	Resource: "myresources",
}

func main() {
	ctx := context.Background()

	// Dynamic clientの作成
	kubeconfigPath := filepath.Join(homedir.HomeDir(), ".kube", "config")
	cfg, _ := clientcmd.BuildConfigFromFlags("", kubeconfigPath)
	dynamicClient, _ := dynamic.NewForConfig(cfg)

	resourceClient := dynamicClient.Resource(myResourceGVR).Namespace(namespace)

	// カスタムリソースを複数作成
	resourceNames := []string{"sample-resource-1", "sample-resource-2", "sample-resource-3"}
	for i, name := range resourceNames {
		resource := &unstructured.Unstructured{
			Object: map[string]interface{}{
				"apiVersion": "example.com/v1",
				"kind":       "MyResource",
				"metadata": map[string]interface{}{
					"name":      name,
					"namespace": namespace,
				},
				"spec": map[string]interface{}{
					"field1": fmt.Sprintf("value-%d", i+1),
					"field2": (i + 1) * 100,
				},
			},
		}
		_, err := resourceClient.Create(ctx, resource, metav1.CreateOptions{})
		if err != nil {
			fmt.Printf("Error creating resource %s: %v\n", name, err)
		}
	}

	// リソース一覧を取得
	resourceList, _ := resourceClient.List(ctx, metav1.ListOptions{})
	for _, item := range resourceList.Items {
		name := item.GetName()
		spec, _ := item.Object["spec"].(map[string]interface{})
		field1, _ := spec["field1"].(string)
		field2, _ := spec["field2"].(int64)

		fmt.Printf("  - Name: %s, Field1: %s, Field2: %d\n", name, field1, field2)
	}

	// 作成したリソースを削除
	for _, name := range resourceNames {
		err := resourceClient.Delete(ctx, name, metav1.DeleteOptions{})
		if err != nil {
			fmt.Printf("Error deleting resource %s: %v\n", name, err)
		}
	}
}
