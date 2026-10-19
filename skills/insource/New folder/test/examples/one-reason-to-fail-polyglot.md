# One Reason to Fail — Polyglot Walkthrough

**Principle:** A test asserts a single coherent behavioral claim. Multiple assertions are acceptable only when they all serve that same claim.

## Anti-pattern (mega-test)
```text
test "user registration works" {
  // creates user
  // checks email sent
  // checks welcome points awarded
  // checks audit log written
  // checks rate-limit not exceeded
}
```
Failure of any one claim is ambiguous.

## Polyglot standard — one claim per test

### TypeScript (Jest / Vitest)
```typescript
it('rejects expired token with 401', async () => {
  const token = TokenFactory.expired();
  const res = await request(app).get('/me').set('Authorization', `Bearer ${token}`);
  expect(res.status).toBe(401);
});

it('accepts valid token and returns user profile', async () => {
  const token = TokenFactory.valid();
  const res = await request(app).get('/me').set('Authorization', `Bearer ${token}`);
  expect(res.status).toBe(200);
  expect(res.body).toMatchObject({ id: expect.any(String), email: expect.any(String) });
});
```

### Python (pytest)
```python
def test_expired_token_is_rejected_with_401(client):
    token = TokenFactory.expired()
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

def test_valid_token_returns_user_profile(client):
    token = TokenFactory.valid()
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert "email" in response.json()
```

### Go
```go
func TestExpiredTokenIsRejectedWith401(t *testing.T) {
    token := factory.ExpiredToken()
    // ... perform request
    assert.Equal(t, 401, resp.StatusCode)
}

func TestValidTokenReturnsUserProfile(t *testing.T) {
    token := factory.ValidToken()
    // ... perform request
    assert.Equal(t, 200, resp.StatusCode)
    // assert body fields
}
```

### Rust (with rstest or plain)
```rust
#[test]
fn expired_token_is_rejected_with_401() {
    let token = TokenFactory::expired();
    let resp = /* call */;
    assert_eq!(resp.status(), 401);
}

#[test]
fn valid_token_returns_user_profile() {
    let token = TokenFactory::valid();
    let resp = /* call */;
    assert_eq!(resp.status(), 200);
    // assert body
}
```

Multiple related assertions inside one test are fine when they evaluate the **same** claim (e.g. status + shape of a successful profile). Unrelated claims become separate tests.