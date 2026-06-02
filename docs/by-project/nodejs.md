# Patterns from Node.js Ecosystem

Node.js, Redux, and XState demonstrate event-driven and state management patterns at scale.

| Pattern | Project | Where | What It Does |
|---------|---------|-------|--------------|
| [Observer / Pub-Sub](/patterns/observer/) | Node.js | `lib/events.js` | `EventEmitter` — foundation of Node's event-driven architecture |
| [Observer / Pub-Sub](/patterns/observer/) | Redux | `createStore.ts` | `subscribe()` + `dispatch()` — state change notification |
| [State Machine](/patterns/state-machine/) | XState | `StateMachine.ts` | Industry-standard finite state machine library |

## Further Reading

- [Node.js (GitHub)](https://github.com/nodejs/node) · [Redux (GitHub)](https://github.com/reduxjs/redux) · [XState (GitHub)](https://github.com/statelyai/xstate)
