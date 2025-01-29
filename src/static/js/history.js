document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const searchInput = document.getElementById('search-input');
    const urgencyFilter = document.getElementById('urgency-filter');
    const dateFilter = document.getElementById('date-filter');
    const conversationList = document.getElementById('conversation-list');
    const conversationTemplate = document.getElementById('conversation-template');
    const conversationModal = document.getElementById('conversation-modal');
    const downloadReportBtn = document.getElementById('download-report');

    let conversations = [];

    // Cargar conversaciones
    function loadConversations() {
        fetch('/api/history')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    conversations = data.conversations;
                    renderConversations(conversations);
                } else {
                    throw new Error(data.error || 'Error al cargar el historial');
                }
            })
            .catch(window.utils.handleError);
    }

    // Renderizar conversaciones
    function renderConversations(conversationsToRender) {
        conversationList.innerHTML = '';
        
        conversationsToRender.forEach(conv => {
            const template = conversationTemplate.content.cloneNode(true);
            
            // Llenar datos
            template.querySelector('.conversation-date').textContent = 
                window.utils.formatDate(conv.date);
            
            const badge = template.querySelector('.badge');
            badge.textContent = conv.urgency_level;
            badge.classList.add(`bg-${window.utils.formatUrgencyLevel(conv.urgency_level)}`);
            
            template.querySelector('.main-concern').textContent = 
                conv.main_concern.substring(0, 100) + (conv.main_concern.length > 100 ? '...' : '');
            
            const viewButton = template.querySelector('.view-details');
            viewButton.onclick = () => showConversationDetails(conv.id);
            
            conversationList.appendChild(template);
        });
    }

    // Mostrar detalles de conversación
    function showConversationDetails(conversationId) {
        fetch(`/api/conversation/${conversationId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const conv = data.conversation;
                    const modalBody = conversationModal.querySelector('.conversation-details');
                    
                    // Construir contenido del modal
                    let content = `
                        <div class="mb-4">
                            <h5>Fecha</h5>
                            <p>${window.utils.formatDate(conv.metadata.timestamp)}</p>
                        </div>
                        <div class="mb-4">
                            <h5>Respuestas</h5>
                            <ul class="list-unstyled">
                    `;
                    
                    for (const [key, value] of Object.entries(conv.responses)) {
                        content += `
                            <li class="mb-2">
                                <strong>${key}:</strong><br>
                                ${value}
                            </li>
                        `;
                    }
                    
                    content += `
                        </ul>
                        </div>
                    `;
                    
                    if (conv.analysis) {
                        content += `
                            <div class="mb-4">
                                <h5>Análisis</h5>
                                <div class="card">
                                    <div class="card-body">
                                        <p><strong>Nivel de urgencia:</strong> 
                                            <span class="badge bg-${window.utils.formatUrgencyLevel(conv.analysis.urgency_level)}">
                                                ${conv.analysis.urgency_level}
                                            </span>
                                        </p>
                                        <p><strong>Principales preocupaciones:</strong></p>
                                        <ul>
                                            ${conv.analysis.main_concerns.map(c => `<li>${c}</li>`).join('')}
                                        </ul>
                                        <p><strong>Recomendaciones:</strong></p>
                                        <ul>
                                            ${conv.analysis.recommendations.map(r => `<li>${r}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                    
                    modalBody.innerHTML = content;
                    
                    // Configurar botón de descarga
                    downloadReportBtn.onclick = () => downloadReport(conversationId);
                    
                    // Mostrar modal
                    const modal = new bootstrap.Modal(conversationModal);
                    modal.show();
                } else {
                    throw new Error(data.error || 'Error al cargar los detalles');
                }
            })
            .catch(window.utils.handleError);
    }

    // Descargar reporte
    function downloadReport(conversationId) {
        fetch(`/api/report/${conversationId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Aquí iría la lógica para descargar el PDF
                    console.log('Descargando reporte:', data.report);
                } else {
                    throw new Error(data.error || 'Error al generar el reporte');
                }
            })
            .catch(window.utils.handleError);
    }

    // Filtrar conversaciones
    function filterConversations() {
        const searchTerm = searchInput.value.toLowerCase();
        const urgency = urgencyFilter.value;
        const dateRange = dateFilter.value;
        
        let filtered = conversations;
        
        // Filtrar por búsqueda
        if (searchTerm) {
            filtered = filtered.filter(conv => 
                conv.main_concern.toLowerCase().includes(searchTerm)
            );
        }
        
        // Filtrar por urgencia
        if (urgency) {
            filtered = filtered.filter(conv => 
                conv.urgency_level === urgency
            );
        }
        
        // Filtrar por fecha
        if (dateRange) {
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            
            filtered = filtered.filter(conv => {
                const convDate = new Date(conv.date);
                switch(dateRange) {
                    case 'today':
                        return convDate >= today;
                    case 'week':
                        const weekAgo = new Date(today);
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        return convDate >= weekAgo;
                    case 'month':
                        const monthAgo = new Date(today);
                        monthAgo.setMonth(monthAgo.getMonth() - 1);
                        return convDate >= monthAgo;
                    default:
                        return true;
                }
            });
        }
        
        renderConversations(filtered);
    }

    // Event listeners
    searchInput.addEventListener('input', filterConversations);
    urgencyFilter.addEventListener('change', filterConversations);
    dateFilter.addEventListener('change', filterConversations);

    // Cargar conversaciones al inicio
    loadConversations();
}); 