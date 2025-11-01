document.addEventListener("DOMContentLoaded", () => {
  // Elementos da página de resultados
  const exportPdfBtn = document.getElementById("export-pdf");
  const exportDocxBtn = document.getElementById("export-docx");
  const copyTextBtn = document.getElementById("copy-text");
  
  // Formato de data YYYY-MM-DD
  function hoje() {
    return new Date().toISOString().slice(0, 10);
  }

  // -------------------------
  // Copiar Texto
  // -------------------------
  if (copyTextBtn) {
    copyTextBtn.addEventListener("click", () => {
      let contentToCopy = "";
      
      // Seleciona o conteúdo baseado no tipo de resultado
      const resultSection = document.querySelector(".text-analysis-content, .translation-content, .ai-check-content, .math-content");
      
      if (resultSection) {
        contentToCopy = resultSection.innerText;
        
        navigator.clipboard.writeText(contentToCopy)
          .then(() => {
            showNotification("Texto copiado para a área de transferência!");
          })
          .catch(err => {
            console.error("Erro ao copiar texto: ", err);
            showNotification("Erro ao copiar texto", true);
          });
      }
    });
  }

  // -------------------------
  // Exportar para PDF
  // -------------------------
  if (exportPdfBtn) {
    exportPdfBtn.addEventListener("click", () => {
      const nome = `resultado_${hoje()}.pdf`;
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();
      
      // Adiciona título
      const title = document.querySelector(".result-title").innerText;
      doc.setFontSize(18);
      doc.text(title, 15, 15);
      
      // Adiciona conteúdo
      const content = document.querySelector(".text-analysis-content, .translation-content, .ai-check-content, .math-content");
      
      if (content) {
        doc.setFontSize(12);
        const lines = doc.splitTextToSize(content.innerText, 180);
        doc.text(lines, 15, 30);
      }
      
      doc.save(nome);
    });
  }

  // -------------------------
  // Exportar para Word
  // -------------------------
  if (exportDocxBtn) {
    exportDocxBtn.addEventListener("click", () => {
      const nome = `resultado_${hoje()}.doc`;
      const content = document.querySelector(".text-analysis-content, .translation-content");
      
      if (content) {
        const html = `
          <html>
            <head><meta charset="utf-8"></head>
            <body>${content.innerHTML}</body>
          </html>`;
        const blob = new Blob([html], { type: "application/msword" });
        downloadFile(blob, nome);
      }
    });
  }

  // -------------------------
  // Funções auxiliares
  // -------------------------
  function downloadFile(blob, filename) {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function showNotification(message, isError = false) {
    const notification = document.createElement("div");
    notification.className = `notification ${isError ? 'error' : 'success'}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add("fade-out");
      setTimeout(() => notification.remove(), 500);
    }, 3000);
  }
});