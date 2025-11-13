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
	var kubeconfigPath *string
	if home := homedir.HomeDir(); home != "" {
		kubeconfigPath = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "kubeconfig file path")
	} else {
		kubeconfigPath = flag.String("kubeconfig", "", "kubeconfig file path")
	}
	flag.Parse()

	// Dynamic clientの作成
	cfg, err := clientcmd.BuildConfigFromFlags("", *kubeconfigPath)
	if err != nil {
		os.Exit(1)
	}

	dynamicClient, err := dynamic.NewForConfig(cfg)
	if err != nil {
		os.Exit(1)
	}

	ctx := context.Background()
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
		unstructuredObj, err := runtime.DefaultUnstructuredConverter.ToUnstructured(resource)
		if err != nil {
			continue
		}
		_, err = resourceClient.Create(ctx, &unstructured.Unstructured{Object: unstructuredObj}, metav1.CreateOptions{})
		if err != nil {
			continue
		}
	}

	// リソース一覧を取得
	time.Sleep(2 * time.Second)

	resourceList, err := resourceClient.List(ctx, metav1.ListOptions{})
	if err != nil {
		os.Exit(1)
	}
	for _, item := range resourceList.Items {
		var myResource examplev1.MyResource
		err := runtime.DefaultUnstructuredConverter.FromUnstructured(item.Object, &myResource)
		if err != nil {
			continue
		}
		fmt.Printf("  - Name: %s, Field1: %s, Field2: %d\n",
			myResource.Name, myResource.Spec.Field1, myResource.Spec.Field2)
	}

	// 作成したリソースを削除
	time.Sleep(2 * time.Second)

	for _, name := range resourceNames {
		err := resourceClient.Delete(ctx, name, metav1.DeleteOptions{})
		if err != nil {
			continue
		}
	}
}
