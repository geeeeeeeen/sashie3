document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("image-form");
  const imageArea = document.getElementById("images");

  form.addEventListener("submit", function(event) {
    event.preventDefault();
    const formData = new FormData(form);
    fetch("/", {
      method: "POST",
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      imageArea.innerHTML = "";
      ["ALL", "POSITIVE", "NEGATIVE"].forEach(sentiment => {
        const imageUrl = data[sentiment];
        if (imageUrl) {
          const img = document.createElement("img");
          img.src = imageUrl;
          img.alt = `${sentiment} Keyphrase Image`;
          img.className = "img-fluid rounded-lg shadow-lg generated-image";
          imageArea.appendChild(img);
        }
      });
    });
  });
});

