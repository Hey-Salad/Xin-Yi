# Xin Yi WMS - Laura-Styled Command Center

## Overview

A modern, dark-themed operations dashboard for Xin Yi WMS, inspired by Laura's design system and featuring:
- 🎨 **Laura's Design Language** - Dark theme, glass-morphism, cherry red accents
- 🗺️ **Mapbox Integration** - Real-time delivery tracking on dark maps
- 📄 **Document Generation** - One-click PDF generation for all WMS documents
- 📹 **Camera Monitoring** - Integration with reCamera/ESP32 devices (from Laura)
- 🔧 **Device Management** - IoT device monitoring and control
- 👤 **Driver Tracking** - Real-time driver locations and management
- 📧 **Email Automation** - Follow-up emails after deliveries

---

## 🎨 Design System (Ported from Laura)

### Colors
```css
--brand-cherry: #ed4c4c      /* Primary brand color */
--brand-peach: #faa09a        /* Secondary accent */
--brand-light-peach: #ffd0cd  /* Tertiary accent */
--bg-black: #000000           /* Pure black background */
--bg-zinc-900: #18181b        /* Card backgrounds */
--bg-zinc-800: #27272a        /* Hover states */
```

### Typography
- **Font**: Figtree (same as Laura)
- **Headings**: Bold, uppercase with letter-spacing
- **Body**: Regular weight, good line-height

### Components
- **Glass-morphism Cards** - Translucent backgrounds with backdrop blur
- **Smooth Animations** - Hover effects, transitions
- **Dark Maps** - Mapbox dark-v11 style
- **Color-coded Statuses** - Green (success), Red (danger), Orange (warning)

---

## 📂 File Structure

```
frontend/
├── dashboard.html              # Main dashboard (Laura-styled)
├── dashboard.js                # Interactive functionality
├── index.html                  # Original simple dashboard
├── app.js                      # Original app logic
├── style.css                   # Original styles
├── product_detail.html         # Product details page
└── product_detail.js           # Product detail logic
```

---

## 🚀 Features

### 1. Dashboard View
**URL:** `dashboard.html#dashboard`

**Features:**
- Real-time stats cards (Total Stock, Today In/Out, Low Stock Alerts)
- Category distribution pie chart (ECharts)
- 7-day trend line chart
- Delivery tracking map (Mapbox)
- Auto-refresh every 30 seconds

**Data Sources:**
- `/api/wms/dashboard/stats`
- `/api/wms/dashboard/category-distribution`
- `/api/wms/dashboard/weekly-trend`

---

### 2. Document Center
**URL:** `dashboard.html#documents`

**10 Document Types Available:**

#### Receiving Documents
- ✅ **PO Receipt** - Purchase order confirmation
- ✅ **Receiving Report** - Daily receiving summary
- ✅ **Putaway Report** - Storage location tracking

#### Inventory Documents
- ✅ **Inventory Report** - Complete inventory snapshot (auto-generate from DB)
- ✅ **Stock Status** - Stock levels with alerts (auto-generate from DB)
- ✅ **Cycle Count** - Physical vs system count

#### Fulfillment Documents
- ✅ **Pick List** - Warehouse picking instructions
- ✅ **Packing Slip** - Shipment contents
- ✅ **Shipping Label** - Address label (4x6")
- ✅ **Bill of Lading** - Freight documentation

**One-Click Generation:**
```javascript
// Auto-generates from database
generateDoc('inventory-report');  // → Downloads PDF

// Uses mock data (customize for your needs)
generateDoc('pick-list');         // → Downloads PDF
```

---

### 3. Delivery Tracking
**URL:** `dashboard.html#deliveries`

**Features:**
- Mapbox dark theme map
- Real-time driver locations
- Delivery status markers (green = delivered, red = in transit)
- Click markers for details (driver, ETA, temperature)
- GPS tracking updates

**Integration Points:**
```javascript
// Add your delivery API
async function loadDeliveryLocations() {
    const deliveries = await fetch('/api/deliveries').then(r => r.json());

    deliveries.forEach(delivery => {
        // Add marker to map
        new mapboxgl.Marker()
            .setLngLat([delivery.lon, delivery.lat])
            .addTo(map);
    });
}
```

---

### 4. Camera Monitoring (from Laura)
**URL:** `dashboard.html#cameras`

**Features:**
- Live camera streams (reCamera/ESP32)
- AI object detection (YOLO11n)
- Gimbal control (preset positions)
- Temperature monitoring
- Motion detection alerts

**reCamera Integration:**
```javascript
// Camera streaming
const cameraStream = `rtsp://[CAMERA-IP]:554/stream`;

// Gimbal control
fetch('http://[CAMERA-IP]:1880/gimbal/preset/1', { method: 'POST' });

// AI detection webhook
POST http://[CAMERA-IP]:1880/ai/detect
Body: { "image": "base64..." }
```

---

### 5. Device Management (IoT)
**URL:** `dashboard.html#devices`

**Features:**
- Meshtastic device monitoring (from Laura)
- ESP32 camera devices
- Temperature sensors
- Battery levels
- Signal strength
- GPS locations
- Device commands

**Device Types:**
- 📡 Meshtastic LoRa nodes
- 📹 reCamera devices
- 🌡️ Temperature sensors
- 📍 GPS trackers

---

### 6. Driver Management
**URL:** `dashboard.html#drivers`

**Features:**
- Driver roster
- Real-time locations on map
- Delivery assignments
- Performance metrics
- Contact management
- Voice calls (Twilio integration from Laura)

**Follow-up Emails:**
```javascript
// Send thank you email after delivery
async function sendFollowUpEmail(deliveryId) {
    await fetch('/api/communication/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            to: 'customer@example.com',
            template: 'delivery_complete',
            data: {
                deliveryId,
                driver: 'Wang Li',
                eta_met: true
            }
        })
    });
}
```

---

### 7. Inventory View
**URL:** `dashboard.html#inventory`

**Features:**
- Complete material list
- Search and filter
- Stock status indicators
- Quick actions (Stock In/Out)
- Low stock alerts
- Product images from Supabase

---

## 🔧 Setup Instructions

### 1. Configure Mapbox (for Maps)

```javascript
// In dashboard.js, line 7:
const MAPBOX_TOKEN = 'pk.eyJ1...your_token_here';
```

**Get Token:**
1. Sign up at https://www.mapbox.com/
2. Create a new token
3. Copy public token to `dashboard.js`

---

### 2. Configure Backend

Ensure your backend is running:
```bash
cd /home/admin/Xin-Yi/backend
python app_platform.py
```

Backend should be accessible at: `http://localhost:2124`

---

### 3. Open Dashboard

```bash
# Option 1: Simple HTTP server
cd /home/admin/Xin-Yi/frontend
python3 -m http.server 8080

# Option 2: Node.js http-server
npx http-server -p 8080

# Then open browser:
open http://localhost:8080/dashboard.html
```

---

### 4. Configure Cameras (Optional)

**For reCamera Integration:**
1. Deploy Node-RED flow from Laura:
   ```bash
   # Copy from Laura project
   cp /home/admin/Laura/recamera-ultimate-complete.json ./
   ```

2. Import to Node-RED at `http://[CAMERA-IP]:1880`

3. Configure camera endpoints in dashboard.js:
   ```javascript
   const CAMERA_ENDPOINTS = {
       camera1: 'http://192.168.1.106:1880',
       camera2: 'http://192.168.1.107:1880'
   };
   ```

---

## 📊 API Endpoints Used

### WMS APIs
```
GET  /api/wms/dashboard/stats
GET  /api/wms/dashboard/category-distribution
GET  /api/wms/dashboard/weekly-trend
GET  /api/wms/materials/all
```

### Document APIs
```
GET  /api/documents/inventory/inventory-report
GET  /api/documents/inventory/stock-status
POST /api/documents/fulfillment/pick-list
POST /api/documents/receiving/po-receipt
```

### Communication APIs (from HeySalad Platform)
```
POST /api/communication/send-email
POST /api/communication/send-sms
```

---

## 🎯 Laura Features Ported

### From Laura Command Center:

✅ **Dark Theme** - Black background, glass-morphism
✅ **Mapbox Integration** - Dark maps for delivery tracking
✅ **Real-time Updates** - SSE/WebSocket support ready
✅ **Driver Management** - Roster with Twilio voice calls
✅ **IoT Devices** - Meshtastic device monitoring
✅ **Camera Integration** - reCamera with AI detection
✅ **Figtree Font** - Professional typography
✅ **Cherry Red Branding** - Consistent color scheme
✅ **Glass Cards** - Translucent backgrounds with blur
✅ **Toast Notifications** - Smooth toast messages
✅ **Responsive Design** - Mobile-friendly layout

### New Xin Yi Features:

🆕 **Document Generation** - 10 WMS document types
🆕 **Inventory Management** - Food inventory with FEFO
🆕 **Stock Tracking** - In/Out operations
🆕 **Product Catalog** - Supabase-hosted images
🆕 **Lot Tracking** - Expiration date management
🆕 **Category Analytics** - Distribution charts
🆕 **7-Day Trends** - Historical data visualization

---

## 🔌 Integration with Laura Services

### 1. Email Follow-ups (SendGrid)

```javascript
// After delivery completion
async function onDeliveryComplete(delivery) {
    // Send thank you email
    await fetch('http://localhost:2124/api/communication/send-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            to: delivery.customer_email,
            from_name: 'Xin Yi Warehouse',
            subject: 'Your delivery has arrived!',
            html: `
                <h2>Thank you for your order!</h2>
                <p>Your delivery from ${delivery.driver_name} has been completed.</p>
                <p><strong>Delivery Details:</strong></p>
                <ul>
                    <li>Order: ${delivery.order_number}</li>
                    <li>Delivered: ${new Date().toLocaleString()}</li>
                    <li>Items: ${delivery.items_count}</li>
                </ul>
                <p>Thank you for choosing Xin Yi!</p>
            `
        })
    });
}
```

### 2. SMS Notifications (Twilio)

```javascript
// Notify driver of new delivery
async function assignDelivery(driverId, orderId) {
    await fetch('http://localhost:2124/api/communication/send-sms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            to: driver.phone,
            message: `New delivery assigned: Order #${orderId}. Check dashboard for details.`
        })
    });
}
```

### 3. Voice Calls (Twilio)

```javascript
// Emergency contact to driver
async function callDriver(driverId) {
    await fetch('http://localhost:2124/api/communication/call-driver', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            driver_id: driverId,
            message: 'Please call warehouse immediately regarding your current delivery.'
        })
    });
}
```

---

## 🚧 Future Enhancements

### High Priority
1. ✨ **Live Camera Feeds** - Embed reCamera streams
2. ✨ **Driver Mobile App** - React Native with GPS tracking
3. ✨ **Automated Emails** - Trigger on delivery events
4. ✨ **Real-time Tracking** - WebSocket updates
5. ✨ **Geofencing** - Alert when deliveries enter/exit zones

### Medium Priority
6. ✨ **Voice Commands** - AI assistant for warehouse
7. ✨ **Barcode Scanning** - Mobile app for pick lists
8. ✨ **Analytics Dashboard** - Delivery performance metrics
9. ✨ **Customer Portal** - Track deliveries in real-time
10. ✨ **Route Optimization** - AI-powered delivery routes

### Low Priority
11. ✨ **Multi-warehouse** - Support multiple locations
12. ✨ **Mobile Dashboard** - PWA for on-the-go access
13. ✨ **API Keys Management** - Secure key rotation
14. ✨ **Audit Logs** - Complete activity tracking

---

## 📱 Mobile Responsiveness

The dashboard is fully responsive:
- **Desktop**: Full sidebar + map
- **Tablet**: Collapsible sidebar
- **Mobile**: Bottom navigation

```css
@media (max-width: 768px) {
    /* Sidebar hidden, hamburger menu */
    /* Grid becomes single column */
    /* Map height reduced */
}
```

---

## 🎨 Customization

### Change Brand Colors

```css
/* In dashboard.html <style> section */
:root {
    --brand-cherry: #YOUR_COLOR;      /* Primary */
    --brand-peach: #YOUR_COLOR;        /* Secondary */
    --brand-light-peach: #YOUR_COLOR;  /* Tertiary */
}
```

### Add Custom Pages

```javascript
// 1. Add navigation item
<a href="#custom" class="nav-item" data-page="custom">
    <span class="nav-icon">🎯</span>
    <span>Custom Page</span>
</a>

// 2. Add view container
<div id="custom-view" class="view-container" style="display: none;">
    <!-- Your content -->
</div>

// 3. Add load function
function loadCustom() {
    console.log('Loading custom page...');
    // Your logic
}
```

---

## 🐛 Troubleshooting

### Map Not Loading
```
Error: Mapbox token not configured
Fix: Set MAPBOX_TOKEN in dashboard.js
```

### Documents Not Generating
```
Error: Backend not accessible
Fix: Ensure backend running on port 2124
```

### Cameras Not Connecting
```
Error: reCamera offline
Fix: Check camera IP, Node-RED status
```

### Styles Not Applying
```
Error: Font not loading
Fix: Check internet connection for Google Fonts
```

---

## 📚 Related Documentation

- **WMS_DOCUMENTS_GUIDE.md** - Document generation system
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **README_PLATFORM.md** - Platform overview
- **/home/admin/Laura/README.md** - Laura Command Center

---

## ✅ Success Checklist

- [x] Laura dark theme applied
- [x] Mapbox integration ready
- [x] Document generation functional
- [x] Glass-morphism UI components
- [x] Real-time stats dashboard
- [x] Category/trend charts
- [x] Navigation system
- [x] Toast notifications
- [x] Responsive layout
- [ ] Mapbox token configured
- [ ] Camera feeds connected
- [ ] Email system tested
- [ ] SMS notifications active
- [ ] Driver tracking live

---

## 🎉 You're Ready!

Your Xin Yi WMS now has a stunning Laura-styled command center!

**Next Steps:**
1. Configure your Mapbox token
2. Test document generation
3. Connect cameras (optional)
4. Set up email/SMS (optional)
5. Customize for your warehouse

---

**Version:** 1.0.0
**Inspired by:** Laura Command Center
**Built for:** Xin Yi WMS
**Design:** Dark theme, glass-morphism, cherry red
