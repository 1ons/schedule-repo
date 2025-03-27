function togglePopup() {
    let botBlock = document.getElementById("tg-bot-block");
  
    if (botBlock.classList.contains("visible")) {
      botBlock.classList.remove("visible");
      setTimeout(() => botBlock.style.bottom = "-150px", 400); // Убираем вниз
    } else {
      botBlock.style.bottom = "20px"; // Поднимаем вверх
      botBlock.classList.add("visible");
    }
  }
  