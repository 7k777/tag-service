// 找到“添加标签”按钮
const showFormButton = document.querySelector("#show-form-button");

// 找到添加标签的表单
const tagForm = document.querySelector("#tag-form");

// 监听按钮的点击动作
showFormButton.addEventListener("click", () => {
  tagForm.classList.toggle("hidden");
});
// 找到正文输入框、标签输入框和卡片列表
const contentInput = document.querySelector("#tag-content");
const labelInput = document.querySelector("#tag-label");
const tagList = document.querySelector(".tag-list");

// 从浏览器里读取以前保存的标签
const savedTags = JSON.parse(localStorage.getItem("myTags")) || [];

// 把一条数据变成卡片，显示在页面上
function showTag(tag) {
  const card = document.createElement("article");
  card.classList.add("tag-card");

  const content = document.createElement("p");
  content.textContent = tag.content;

  const label = document.createElement("span");
  label.textContent = `#${tag.label}`;

  card.append(content, label);
  tagList.prepend(card);
}

// 页面打开时，显示以前保存的标签
savedTags.forEach(showTag);

// 监听表单提交
tagForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const content = contentInput.value.trim();
  const label = labelInput.value.trim();

  if (!content || !label) {
    alert("正文和标签都要填写哦");
    return;
  }

  const newTag = {
    content: content,
    label: label
  };

  savedTags.push(newTag);
  localStorage.setItem("myTags", JSON.stringify(savedTags));

  showTag(newTag);

  tagForm.reset();
  tagForm.classList.add("hidden");
});