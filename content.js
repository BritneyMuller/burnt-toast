// content.js
  // Burnt Toast AI Replacer - An Orange Labs Project by Britney Muller
  // Replaces all instances of "AI" with "burnt toast" on web pages
  
  function replaceTextInNode(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      // Replace all instances of "AI" (case insensitive) with "burnt toast"
      node.textContent = node.textContent.replace(/\bAI\b/gi, 'burnt toast');
    } else {
      // Skip script and style elements
      if (node.tagName && (node.tagName === 'SCRIPT' || node.tagName === 'STYLE')) {
        return;
      }
      
      // Recursively process child nodes
      for (let i = 0; i < node.childNodes.length; i++) {
        replaceTextInNode(node.childNodes[i]);
      }
    }
  }
  
  // Replace text in the current document
  replaceTextInNode(document.body);
  
  // Watch for dynamically added content
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (node.nodeType === Node.ELEMENT_NODE || node.nodeType === Node.TEXT_NODE) {
          replaceTextInNode(node);
        }
      });
    });
  });
  
  // Start observing
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });