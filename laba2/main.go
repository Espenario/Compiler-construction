package main

import (
	"go/ast"
	"go/token"
)

func main(file *ast.File) {
	ast.Inspect(file, func(node ast.Node) bool {
		if basicLit, ok := node.(*ast.BasicLit); ok {
			if basicLit.Kind == token.STRING {
				basicLit.Value = "POPAAAA"
			}
		}
		return true
	})
}
