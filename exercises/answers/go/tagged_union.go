package answers

import "fmt"

type Tag int

const (
	TagNull Tag = iota
	TagBool
	TagNumber
	TagString
)

type TaggedValue struct {
	Tag    Tag
	Bool   bool
	Number float64
	Str    string
}

func Display(tv TaggedValue) string {
	switch tv.Tag {
	case TagNull:
		return "null"
	case TagBool:
		if tv.Bool {
			return "true"
		}
		return "false"
	case TagNumber:
		return fmt.Sprintf("%g", tv.Number)
	case TagString:
		return fmt.Sprintf("%q", tv.Str)
	default:
		return "unknown"
	}
}
