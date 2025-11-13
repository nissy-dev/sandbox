package main

import (
	"context"
	"fmt"
	"path/filepath"

	examplev1 "github.com/nissy-dev/sandbox/go-crd-operation/pkg/apis/example.com/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime"
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
		resource := &examplev1.MyResource{
			TypeMeta: metav1.TypeMeta{
				APIVersion: "example.com/v1",
				Kind:       "MyResource",
			},
			ObjectMeta: metav1.ObjectMeta{
				Name:      name,
				Namespace: namespace,
			},
			Spec: examplev1.MyResourceSpec{
				Field1: fmt.Sprintf("value-%d", i+1),
				Field2: int32((i + 1) * 100),
			},
		}
		unstructuredObj, _ := runtime.DefaultUnstructuredConverter.ToUnstructured(resource)
		_, _ = resourceClient.Create(ctx, &unstructured.Unstructured{Object: unstructuredObj}, metav1.CreateOptions{})
	}

	// リソース一覧を取得
	resourceList, _ := resourceClient.List(ctx, metav1.ListOptions{})
	for _, item := range resourceList.Items {
		var myResource examplev1.MyResource
		_ = runtime.DefaultUnstructuredConverter.FromUnstructured(item.Object, &myResource)
		fmt.Printf("  - Name: %s, Field1: %s, Field2: %d\n",
			myResource.Name, myResource.Spec.Field1, myResource.Spec.Field2)
	}

	// 作成したリソースを削除
	for _, name := range resourceNames {
		_ = resourceClient.Delete(ctx, name, metav1.DeleteOptions{})
	}
}
