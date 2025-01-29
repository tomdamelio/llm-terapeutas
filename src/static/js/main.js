// Funciones de utilidad comunes
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatUrgencyLevel(level) {
    const badges = {
        'ALTO': 'danger',
        'MEDIO': 'warning',
        'BAJO': 'success'
    };
    return badges[level] || 'secondary';
}

// Manejo de errores
function handleError(error) {
    console.error('Error:', error);
    // Aquí podrías mostrar un toast o notificación al usuario
}

// Animaciones
function fadeIn(element, duration = 500) {
    element.style.opacity = 0;
    element.style.display = 'block';
    
    let start = null;
    function animate(currentTime) {
        if (!start) start = currentTime;
        const progress = currentTime - start;
        
        element.style.opacity = Math.min(progress / duration, 1);
        
        if (progress < duration) {
            requestAnimationFrame(animate);
        }
    }
    requestAnimationFrame(animate);
}

function fadeOut(element, duration = 500) {
    let start = null;
    function animate(currentTime) {
        if (!start) start = currentTime;
        const progress = currentTime - start;
        
        element.style.opacity = Math.max(1 - (progress / duration), 0);
        
        if (progress < duration) {
            requestAnimationFrame(animate);
        } else {
            element.style.display = 'none';
        }
    }
    requestAnimationFrame(animate);
}

// Exportar funciones para uso en otros archivos
window.utils = {
    formatDate,
    formatUrgencyLevel,
    handleError,
    fadeIn,
    fadeOut
}; 