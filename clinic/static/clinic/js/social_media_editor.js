(function () {
  function loadImage(src) {
    return new Promise(function (resolve, reject) {
      var image = new Image();
      image.onload = function () { resolve(image); };
      image.onerror = reject;
      image.src = src;
    });
  }

  function numericInput(root, name) {
    var input = root.querySelector('[data-control="' + name + '"]');
    return input ? parseFloat(input.value || "0") : 0;
  }

  function drawCover(ctx, image, slot, zoom, offsetX, offsetY) {
    var scale = Math.max(slot.w / image.naturalWidth, slot.h / image.naturalHeight) * zoom;
    var drawW = image.naturalWidth * scale;
    var drawH = image.naturalHeight * scale;
    var drawX = slot.x + (slot.w - drawW) / 2 + offsetX;
    var drawY = slot.y + (slot.h - drawH) / 2 + offsetY;

    ctx.save();
    ctx.beginPath();
    ctx.rect(slot.x, slot.y, slot.w, slot.h);
    ctx.clip();
    ctx.drawImage(image, drawX, drawY, drawW, drawH);
    ctx.restore();
  }

  function restoreFrame(ctx, slot, frame) {
    var frameRight = frame.x + frame.w;
    var frameBottom = frame.y + frame.h;
    var slotRight = slot.x + slot.w;
    var slotBottom = slot.y + slot.h;

    ctx.save();
    ctx.fillStyle = "#ffffff";
    if (slot.y > frame.y) ctx.fillRect(frame.x, frame.y, frame.w, slot.y - frame.y);
    if (slotBottom < frameBottom) ctx.fillRect(frame.x, slotBottom, frame.w, frameBottom - slotBottom);
    if (slot.x > frame.x) ctx.fillRect(frame.x, frame.y, slot.x - frame.x, frame.h);
    if (slotRight < frameRight) ctx.fillRect(slotRight, frame.y, frameRight - slotRight, frame.h);
    ctx.restore();
  }

  function resetControls(root, prefix) {
    var defaults = {
      zoom: "1",
      x: "0",
      y: "0"
    };
    Object.keys(defaults).forEach(function (key) {
      var input = root.querySelector('[data-control="' + prefix + "_" + key + '"]');
      if (input) input.value = defaults[key];
    });
  }

  function initEditor(root) {
    var canvas = root.querySelector("canvas");
    var slotsNode = document.getElementById(root.dataset.slotsId);
    var framesNode = document.getElementById(root.dataset.framesId);
    if (!canvas || !slotsNode) return;

    var ctx = canvas.getContext("2d");
    var slots = JSON.parse(slotsNode.textContent);
    var frames = framesNode ? JSON.parse(framesNode.textContent) : {};
    var images = {};

    function draw() {
      if (!images.template || !images.before || !images.after) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(images.template, 0, 0, canvas.width, canvas.height);

      drawCover(
        ctx,
        images.before,
        slots.before,
        numericInput(root, "before_zoom"),
        numericInput(root, "before_x"),
        numericInput(root, "before_y")
      );
      if (frames.before) restoreFrame(ctx, slots.before, frames.before);
      drawCover(
        ctx,
        images.after,
        slots.after,
        numericInput(root, "after_zoom"),
        numericInput(root, "after_x"),
        numericInput(root, "after_y")
      );
      if (frames.after) restoreFrame(ctx, slots.after, frames.after);
    }

    Promise.all([
      loadImage(root.dataset.templateUrl),
      loadImage(root.dataset.beforeUrl),
      loadImage(root.dataset.afterUrl)
    ]).then(function (loaded) {
      images.template = loaded[0];
      images.before = loaded[1];
      images.after = loaded[2];
      draw();
    });

    root.querySelectorAll("[data-control]").forEach(function (input) {
      input.addEventListener("input", draw);
    });

    root.querySelectorAll("[data-reset]").forEach(function (button) {
      button.addEventListener("click", function () {
        resetControls(root, button.dataset.reset);
        draw();
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-social-editor]").forEach(initEditor);
  });
})();
