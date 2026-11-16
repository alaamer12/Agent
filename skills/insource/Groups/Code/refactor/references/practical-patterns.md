# Practical Patterns (Quick Reference)

> Quick before/after sketches for the moves the skill reaches for first. Load only the one you are about to apply.
> Overview lives in [`../SKILL.md`](../SKILL.md).

## Table of Contents
1. [Extract Method (the workhorse)](#extract-method-the-workhorse)
2. [Guard Clauses over Nested Conditionals](#guard-clauses-over-nested-conditionals)
3. [Parameter Object / Domain Types](#parameter-object--domain-types)
4. [Strategy over Type Switch](#strategy-over-type-switch)

---

## Extract Method (the workhorse)

```diff
- async function processOrder(orderId) {
-   // 50 lines fetch + validate + price + inventory + ship + notify
- }
+ async function processOrder(orderId) {
+   const order = await fetchOrder(orderId);
+   validateOrder(order);
+   const pricing = calculatePricing(order);
+   await updateInventory(order);
+   const shipment = await createShipment(order);
+   await sendNotifications(order, pricing, shipment);
+   return { order, pricing, shipment };
+ }
```

---

## Guard Clauses over Nested Conditionals

```diff
- function process(order) {
-   if (order) {
-     if (order.user) {
-       if (order.user.isActive) {
-         if (order.total > 0) return processOrder(order);
-         else return { error: 'Invalid total' };
-       } ...
- }
+ function process(order) {
+   if (!order) return { error: 'No order' };
+   if (!order.user) return { error: 'No user' };
+   if (!order.user.isActive) return { error: 'User inactive' };
+   if (order.total <= 0) return { error: 'Invalid total' };
+   return processOrder(order);
+ }
```

---

## Parameter Object / Domain Types

```diff
- function createUser(email, password, name, age, address, city, country, phone) { ... }
+ interface UserData {
+   email: string;
+   password: string;
+   name: string;
+   age?: number;
+   address?: Address;
+   phone?: string;
+ }
+ function createUser(data: UserData) { ... }
```

---

## Strategy over Type Switch

When a conditional branches on type or mode and will grow, replace it with Strategy or polymorphism rather than adding another `else if`.

---

Load [`SKILL.md`](../SKILL.md) first — it states the loop, the always-on rules, and how these files fit together.
