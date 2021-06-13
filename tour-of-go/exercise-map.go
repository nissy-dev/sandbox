package main

import (
	"strings"
)

func WordCount(s string) map[string]int {
	m := make(map[string]int)
	for _, w := range strings.Fields(s) {
		m[w]++
	}
	return m
}

// func main() {
// 	fmt.Printf("%#v", WordCount("hello world! I'm a hello world!"))
// }
