package answers

// Go: bounded channels provide backpressure natively
func producer(ch chan<- int) {
	for i := 0; ; i++ {
		ch <- i // blocks when channel is full
	}
}

func consumer(ch <-chan int) {
	for v := range ch {
		fmt.Println(v) // process at consumer's pace
	}
}

func Run() {
	ch := make(chan int, 10) // bounded buffer of 10
	go producer(ch)
	consumer(ch)
}
