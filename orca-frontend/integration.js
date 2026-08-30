document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup UI toggles
    const sosBtn = document.getElementById('fab-sos-btn');
    const sosModal = document.getElementById('modal-sos');
    const sosCancelBtn = document.getElementById('sos-cancel-btn');
    
    let activeIncidentId = null;
    let holdTimer = null;

    if(sosBtn && sosModal) {
        sosBtn.addEventListener('mousedown', startSosHold);
        sosBtn.addEventListener('mouseup', endSosHold);
        sosBtn.addEventListener('mouseleave', endSosHold);
        sosBtn.addEventListener('touchstart', startSosHold, {passive: true});
        sosBtn.addEventListener('touchend', endSosHold, {passive: true});

        function startSosHold() {
            sosBtn.classList.add('animate-pulse');
            holdTimer = setTimeout(() => {
                triggerSosEmergency();
            }, 1000); // 1s hold for triggering
        }

        function endSosHold() {
            clearTimeout(holdTimer);
            sosBtn.classList.remove('animate-pulse');
        }

        async function triggerSosEmergency() {
            try {
                // Default coordinates for testing
                const res = await OrcaAPI.triggerSOS(44.3126, -68.2158);
                activeIncidentId = res.incident_id;
                sosModal.classList.remove('hidden');
                sosModal.classList.add('flex');
            } catch (err) {
                console.error(err);
                alert("SOS Trigger Failed: " + err.message);
            }
        }
    }

    if(sosCancelBtn) {
        let cancelHoldTimer = null;
        sosCancelBtn.addEventListener('mousedown', startCancelHold);
        sosCancelBtn.addEventListener('mouseup', endCancelHold);
        sosCancelBtn.addEventListener('mouseleave', endCancelHold);
        sosCancelBtn.addEventListener('touchstart', startCancelHold, {passive: true});
        sosCancelBtn.addEventListener('touchend', endCancelHold, {passive: true});

        function startCancelHold() {
            sosCancelBtn.classList.add('opacity-50');
            cancelHoldTimer = setTimeout(() => {
                cancelSosEmergency();
            }, 3000); // 3-second hold to cancel as user suggested
        }

        function endCancelHold() {
            clearTimeout(cancelHoldTimer);
            sosCancelBtn.classList.remove('opacity-50');
        }

        async function cancelSosEmergency() {
            if(!activeIncidentId) return;
            try {
                await OrcaAPI.cancelSOS(activeIncidentId);
                sosModal.classList.add('hidden');
                sosModal.classList.remove('flex');
                activeIncidentId = null;
                alert("SOS Cancelled successfully.");
            } catch (err) {
                console.error(err);
                alert("Failed to cancel SOS: " + err.message);
            }
        }
    }

    // 2. Load and Log Trips
    const openTripBtn = document.getElementById('fab-trip-btn');
    const tripPanel = document.getElementById('panel-trip');
    const closeTripBtn = document.getElementById('trip-close-btn');
    const saveLogBtn = document.getElementById('trip-save-log');

    if(openTripBtn && tripPanel) {
        openTripBtn.addEventListener('click', async () => {
            tripPanel.classList.remove('hidden');
            try {
                const tripData = await OrcaAPI.getTrip('TRP-1001');
                console.log("Trip Loaded:", tripData);
                document.getElementById('trip-heading').textContent = "Heading: " + tripData.vessel_details.heading + "°";
            } catch (err) {
                console.error(err);
            }
        });
        
        closeTripBtn.addEventListener('click', () => {
            tripPanel.classList.add('hidden');
        });
        
        if (saveLogBtn) {
            saveLogBtn.addEventListener('click', async () => {
                const activityType = document.getElementById('activity-type').value;
                const notes = document.getElementById('log-notes').value;
                saveLogBtn.textContent = "Saving...";
                try {
                    await OrcaAPI.logTripAction('TRP-1001', 44.3126, -68.2158, activityType, notes);
                    alert("Log entry saved!");
                    document.getElementById('log-notes').value = "";
                } catch(e) {
                    alert("Failed to save: " + e.message);
                } finally {
                    saveLogBtn.textContent = "Save Entry";
                }
            });
        }
    }

    // 3. Alerts and Advisories
    const openAlertsBtn = document.getElementById('fab-alerts-btn');
    const alertsPanel = document.getElementById('panel-alerts');
    const closeAlertsBtn = document.getElementById('alerts-close-btn');

    if(openAlertsBtn && alertsPanel) {
        openAlertsBtn.addEventListener('click', async () => {
            alertsPanel.classList.remove('hidden');
            try {
                const alertsData = await OrcaAPI.getRegionalAlerts('Sector 7G');
                console.log("Alerts Loaded:", alertsData);
                // Dynamically populate if necessary
            } catch (err) {
                console.error(err);
            }
        });

        closeAlertsBtn.addEventListener('click', () => {
            alertsPanel.classList.add('hidden');
        });
    }
    
    // Automatically fetch Advisory and show if stale/offline
    async function checkAdvisory() {
        try {
            if (typeof OrcaAPI !== 'undefined' && typeof OrcaAPI.getLastKnownAdvisory === 'function') {
                const adv = await OrcaAPI.getLastKnownAdvisory();
                if(adv.status === "stale") {
                    const advisoryCard = document.getElementById('advisory-stale-card');
                    if(advisoryCard) {
                        advisoryCard.classList.remove('hidden');
                    }
                }
            }
        } catch(e) {
            console.error(e);
        }
    }
    
    // check on load
    checkAdvisory();
});
