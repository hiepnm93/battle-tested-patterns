type Tag = 'null' | 'boolean' | 'number' | 'string' | 'array' | 'object';

interface TaggedValue {
  tag: Tag;
  value: null | boolean | number | string | TaggedValue[] | Record<string, TaggedValue>;
}

function stringify(tv: TaggedValue): string {
  switch (tv.tag) {
    case 'null': return 'null';
    case 'boolean': return String(tv.value);
    case 'number': return String(tv.value);
    case 'string': return `"${tv.value}"`;
    case 'array': {
      const items = (tv.value as TaggedValue[]).map(stringify);
      return `[${items.join(',')}]`;
    }
    case 'object': {
      const obj = tv.value as Record<string, TaggedValue>;
      const pairs = Object.keys(obj).map(k => `"${k}":${stringify(obj[k])}`);
      return `{${pairs.join(',')}}`;
    }
  }
}
