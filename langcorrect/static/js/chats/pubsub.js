export const pubSub = {
  events: {},
  subscribe: function (eventName, fn) {
    console.log(`🚀 [PUBSUB] Someone just subscribed to know about`, eventName);
    this.events[eventName] = this.events[eventName] || [];
    this.events[eventName].push(fn);
  },
  unsubscribe: function (eventName, fn) {
    console.log(`🚀 [PUBSUB] Someone just Unsubscribed from`, eventName);
    if (!this.events[eventName]) return;
    this.events[eventName] = this.events[eventName].filter((f) => f !== fn);
  },
  publish: function (eventName, data) {
    console.log(
      `🚀 [PUBSUB] Making a broadcast about`,
      eventName,
      `with`,
      data,
    );
    if (!this.events[eventName]) return;
    this.events[eventName].forEach((fn) => fn(data));
  },
};
