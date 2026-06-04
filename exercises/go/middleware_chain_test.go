package exercises

import (
	"strings"
	"testing"
)

type Context struct {
	Request  string
	Response string
	Log      []string
}

type Middleware func(ctx *Context, next func())

type Pipeline struct {
	middlewares []Middleware
}

func NewPipeline() *Pipeline {
	return &Pipeline{}
}

func (p *Pipeline) Use(mw Middleware) {
	p.middlewares = append(p.middlewares, mw)
}

func (p *Pipeline) Execute(ctx *Context) {
	index := 0
	var run func()
	run = func() {
		if index < len(p.middlewares) {
			mw := p.middlewares[index]
			index++
			mw(ctx, run)
		}
	}
	run()
}

func TestMiddlewareOrder(t *testing.T) {
	p := NewPipeline()
	p.Use(func(ctx *Context, next func()) {
		ctx.Log = append(ctx.Log, "A-before")
		next()
		ctx.Log = append(ctx.Log, "A-after")
	})
	p.Use(func(ctx *Context, next func()) {
		ctx.Log = append(ctx.Log, "B-before")
		next()
		ctx.Log = append(ctx.Log, "B-after")
	})
	p.Use(func(ctx *Context, next func()) {
		ctx.Log = append(ctx.Log, "handler")
		ctx.Response = "OK"
	})

	ctx := &Context{Request: "test"}
	p.Execute(ctx)

	want := "A-before,B-before,handler,B-after,A-after"
	got := strings.Join(ctx.Log, ",")
	if got != want {
		t.Errorf("got %q, want %q", got, want)
	}
}

func TestMiddlewareShortCircuit(t *testing.T) {
	p := NewPipeline()
	p.Use(func(ctx *Context, next func()) {
		ctx.Response = "blocked"
		// don't call next()
	})
	p.Use(func(ctx *Context, next func()) {
		ctx.Response = "should not reach"
		next()
	})

	ctx := &Context{}
	p.Execute(ctx)

	if ctx.Response != "blocked" {
		t.Errorf("expected blocked, got %q", ctx.Response)
	}
}

func TestMiddlewareEmpty(t *testing.T) {
	p := NewPipeline()
	ctx := &Context{Request: "test"}
	p.Execute(ctx)
	if ctx.Response != "" {
		t.Error("empty pipeline should not set response")
	}
}
