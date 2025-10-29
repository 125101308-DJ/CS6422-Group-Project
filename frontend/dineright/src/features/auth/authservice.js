export function loginUser(email, password) {
  if (email === "test@gmail.com" && password === "123456") {
    return { code: "SUCCESS", id: 1 };
  } else {
    return { code: "FAIL" };
  }
}
