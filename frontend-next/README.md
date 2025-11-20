# Xin Yi WMS - Next.js Frontend

Modern React-based frontend for the Xin Yi Warehouse Management System, built with Next.js 16, TypeScript, and Tailwind CSS.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## 📦 Tech Stack

- **Next.js 16** - React framework with App Router
- **React 19** - Latest React with Server Components
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Utility-first CSS
- **Lucide React** - Beautiful icon library
- **Recharts** - Chart library for data visualization

## 🏗️ Project Structure

```
frontend-next/
├── app/
│   ├── (dashboard)/          # Dashboard layout group
│   │   ├── dashboard/         # Main dashboard page
│   │   ├── inventory/         # Inventory management
│   │   ├── documents/         # Document generation
│   │   ├── deliveries/        # Delivery tracking
│   │   ├── cameras/           # Camera monitoring
│   │   ├── devices/           # Device management
│   │   ├── drivers/           # Driver management
│   │   └── layout.tsx         # Dashboard layout with sidebar
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Landing page
│   └── globals.css            # Global styles
├── components/
│   ├── Sidebar.tsx            # Navigation sidebar
│   └── StatCard.tsx           # Statistics card component
├── lib/
│   ├── api.ts                 # API client utilities
│   └── types.ts               # TypeScript type definitions
└── public/                    # Static assets
```

## 🎨 Features

### Landing Page
- Modern, animated hero section
- Feature highlights with icons
- Call-to-action buttons
- Responsive design

### Dashboard
- Real-time statistics cards
- 7-day trend charts
- Category distribution
- Auto-refresh every 30 seconds
- Delivery tracking map (coming soon)

### Inventory Management
- Searchable product table
- Product images and details
- Stock status indicators
- Click-through to product details

### Navigation
- Sidebar with icon-based navigation
- Active route highlighting
- Smooth transitions

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:2124/api

# For production:
# NEXT_PUBLIC_API_URL=https://wms.heysalad.app/api
```

### API Endpoints

The application connects to the Xin Yi WMS backend API. Ensure the backend is running on port 2124 (or update the API URL accordingly).

## 🚢 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Cloudflare Pages

```bash
# Build
npm run build

# Deploy the 'out' directory to Cloudflare Pages
```

### Docker

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📝 Development

### Adding New Pages

1. Create a new folder in `app/(dashboard)/`
2. Add a `page.tsx` file
3. Update the navigation in `components/Sidebar.tsx`

### Adding New Components

1. Create component in `components/`
2. Use TypeScript for type safety
3. Follow the existing naming conventions

### API Integration

Use the utilities in `lib/api.ts`:

```typescript
import { apiGet, API_ENDPOINTS } from '@/lib/api';

const data = await apiGet(API_ENDPOINTS.dashboardStats);
```

## 🎯 Roadmap

- [ ] Product detail page
- [ ] Charts with Recharts
- [ ] Delivery map integration
- [ ] Document generation UI
- [ ] Camera feed integration
- [ ] Real-time updates with WebSockets
- [ ] Mobile responsive improvements
- [ ] Dark/Light theme toggle
- [ ] Export functionality
- [ ] Advanced filtering and sorting

## 📄 License

MIT License - see LICENSE file for details

---

Built with ❤️ by HeySalad
