document.addEventListener("DOMContentLoaded", () => {
  // =========================
  // Referências aos elementos principais
  // =========================
  const form = document.querySelector("form");
  const inputArquivo = document.getElementById("file");
  const spanNomeArquivo = document.getElementById("file-name");
  const btnSubmit = document.getElementById("submit");
  const spanTextoAguarde = document.getElementById("txt_aguarde");
  const overlay = document.getElementById("overlay");
  const customOverlay = document.getElementById("customOverlay");
  const customModalText = document.getElementById("customModalText");
  
  // Elementos para mostrar/ocultar sub-opções
  const functionOptions = document.querySelectorAll('input[name="function_option"]');
  const textAnalysisOptions = document.getElementById("text-analysis-options");
  const translationOptions = document.getElementById("translation-options");

  // =========================
  // Toggle das sub-opções
  // =========================
  function toggleSubOptions() {
    const selectedFunction = document.querySelector('input[name="function_option"]:checked').value;
    
    // Oculta todas as sub-opções
    textAnalysisOptions.style.display = "none";
    translationOptions.style.display = "none";
    
    // Mostra apenas as relevantes
    if (selectedFunction === "text_analysis") {
      textAnalysisOptions.style.display = "block";
    } else if (selectedFunction === "translation") {
      translationOptions.style.display = "block";
    }
  }
  
  // Adiciona listeners para mudanças
  functionOptions.forEach(option => {
    option.addEventListener("change", toggleSubOptions);
  });
  
  // Configura estado inicial
  toggleSubOptions();

  // =========================
  // Mostra nome(s) do(s) arquivo(s) escolhido(s)
  // =========================
  inputArquivo.addEventListener("change", () => {
    const nomes = Array.from(inputArquivo.files).map(f => f.name);
    spanNomeArquivo.textContent =
      nomes.length ? nomes.join(", ") : "Nenhum arquivo escolhido";
  });

  // =========================
  // Valida antes de enviar e exibe loading
  // =========================
  form.addEventListener("submit", (e) => {
    if (!inputArquivo.files.length) {
      e.preventDefault();
      showModal("Por favor, selecione pelo menos um arquivo antes de continuar!");
      return;
    }
    
    // Validação adicional para tradução (idioma selecionado)
    const selectedFunction = document.querySelector('input[name="function_option"]:checked').value;
    if (selectedFunction === "translation") {
      const targetLang = document.getElementById("target_lang");
      if (!targetLang.value) {
        e.preventDefault();
        showModal("Por favor, selecione um idioma para tradução!");
        return;
      }
    }
    
    spanTextoAguarde.textContent = "Por favor, aguarde... processando arquivo(s).";
    overlay.style.display = "flex";
    btnSubmit.disabled = true;
  });

  // =========================
  // Limpeza de dados temporários
  // =========================
  function clearTemp() {
    navigator.sendBeacon("/limpar");
  }
  
  clearTemp();
  window.addEventListener("beforeunload", clearTemp);

  // =========================
  // Detecta reload ou back/forward e redireciona
  // =========================
  const navEntries = performance.getEntriesByType("navigation");
  if (navEntries[0] &&
      (navEntries[0].type === "reload" || navEntries[0].type === "back_forward")) {
    clearTemp();
    window.location.href = "/";
    return;
  }

  // =========================
  // Funções auxiliares
  // =========================
  function showModal(message) {
    customModalText.textContent = message;
    customOverlay.style.display = "flex";
  }

  // Fecha modal de erro
  document.querySelector(".close-modal").addEventListener("click", () => {
    customOverlay.style.display = "none";
  });
  
  customOverlay.addEventListener("click", (e) => {
    if (e.target === customOverlay) customOverlay.style.display = "none";
  });
});