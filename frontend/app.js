// 后端地址
const API = "/api";

// token 和邮箱（存在浏览器 localStorage 里，刷新不丢）
let token = localStorage.getItem("token") || "";
let currentEmail = localStorage.getItem("email") || "";

// ============ 视图元素 ============
const loginView = document.querySelector("#login-view");
const registerView = document.querySelector("#register-view");
const tagsView = document.querySelector("#tags-view");
const currentUser = document.querySelector("#current-user");

// ============ 登录 / 注册 / 退出 ============

// 登录
async function login() {
  const email = document.querySelector("#login-email").value.trim();
  const password = document.querySelector("#login-password").value;

  if (!email || !password) {
    alert("邮箱和密码都要填哦");
    return;
  }

  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.detail || "登录失败");
    return;
  }

  const data = await res.json();
  token = data.token;
  currentEmail = data.email;
  localStorage.setItem("token", token);
  localStorage.setItem("email", currentEmail);

  showTagsView();
  loadTags();
}

// 注册
async function register() {
  const email = document.querySelector("#reg-email").value.trim();
  const password = document.querySelector("#reg-password").value;

  if (!email || !password) {
    alert("邮箱和密码都要填哦");
    return;
  }

  const res = await fetch(`${API}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.detail || "注册失败");
    return;
  }

  alert("注册成功！请登录");
  showLoginView();
}

// 退出登录
function logout() {
  token = "";
  currentEmail = "";
  localStorage.removeItem("token");
  localStorage.removeItem("email");
  showLoginView();
}

// ============ 视图切换（三个独立视图） ============

function showLoginView() {
  loginView.classList.remove("hidden");
  registerView.classList.add("hidden");
  tagsView.classList.add("hidden");
}

function showRegisterView() {
  loginView.classList.add("hidden");
  registerView.classList.remove("hidden");
  tagsView.classList.add("hidden");
}

function showTagsView() {
  loginView.classList.add("hidden");
  registerView.classList.add("hidden");
  tagsView.classList.remove("hidden");
  currentUser.textContent = `当前账号：${currentEmail}`;
}

// ============ 带 token 的请求头 ============

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

// ============ tags 相关 ============

const showFormButton = document.querySelector("#show-form-button");
const tagForm = document.querySelector("#tag-form");
const contentInput = document.querySelector("#tag-content");
const labelInput = document.querySelector("#tag-label");
const tagList = document.querySelector(".tag-list");

// 把一条数据变成卡片
function showTag(tag) {
  const card = document.createElement("article");
  card.classList.add("tag-card");

  const content = document.createElement("p");
  content.textContent = tag.content;

  const label = document.createElement("span");
  label.textContent = `#${tag.tags[0]}`;

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "删除";
  deleteButton.classList.add("delete-button");

  deleteButton.addEventListener("click",() => {
    deleteTag(tag.id);
  });

  card.append(content, label,deleteButton);
  tagList.prepend(card);
}

// 从服务器拉列表（带 token）
async function loadTags() {
  const res = await fetch(`${API}/tags`, { headers: authHeaders() });
  const data = await res.json();
  tagList.innerHTML = "";
  data.data.forEach(showTag);
}
async function deleteTag(tagId) {
  const confirmed = confirm("确定要删除这条标签吗？");

  if (!confirmed){
    return;
  }
  const res = await fetch(`${API}/tags/${tagId}`,{
    method:"DELETE",
    headers:authHeaders()
  });

  if (!res.ok){
  alert("删除失败，请稍后重试");
  return;
  }

  loadTags();
}

// ============ 事件绑定 ============

document.querySelector("#login-btn").addEventListener("click", login);
document.querySelector("#register-btn").addEventListener("click", register);
document.querySelector("#logout-btn").addEventListener("click", logout);
document.querySelector("#to-register").addEventListener("click", showRegisterView);
document.querySelector("#to-login").addEventListener("click", showLoginView);

showFormButton.addEventListener("click", () => {
  tagForm.classList.toggle("hidden");
});

tagForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const content = contentInput.value.trim();
  const label = labelInput.value.trim();

  if (!content || !label) {
    alert("正文和标签都要填写哦");
    return;
  }

  const res = await fetch(`${API}/tags`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      content: content,
      tags: [label]
    })
  });

  if (!res.ok) {
    alert("添加失败，请重新登录试试");
    return;
  }

  tagList.innerHTML = "";
  loadTags();

  tagForm.reset();
  tagForm.classList.add("hidden");
});

// ============ 页面加载：有 token 就进 tags，没有就登录 ============

if (token) {
  showTagsView();
  loadTags();
} else {
  showLoginView();
}
