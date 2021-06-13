package main

import (
	"fmt"
	"math"
)

func Sqrt(x float64) float64 {
	z := x / 2.0
	for i := 0; i < 10; i++ {
		diff := (z*z - x) / (2.0 * z)
		z -= diff
		if math.Abs(diff) < 1e-6 {
			break
		}
	}
	return z
}

func main() {
	fmt.Println(Sqrt(3))
}
