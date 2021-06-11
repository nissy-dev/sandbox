package main

func fibonacci() func() int {
	a, b := 1, 0
	return func() int {
		a, b = b, a+b
		return a
	}
}

func fibonacci2(n int) int {
	if n == 1 {
		return 0
	} else if n == 2 {
		return 1
	} else {
		return fibonacci2(n-1) + fibonacci2(n-2)
	}
}

// func main() {
// 	f := fibonacci()
// 	for i := 0; i < 10; i++ {
// 		fmt.Println(f())
// 	}

// 	for i := 0; i < 10; i++ {
// 		fmt.Println(fibonacci2(i + 1))
// 	}
// }
