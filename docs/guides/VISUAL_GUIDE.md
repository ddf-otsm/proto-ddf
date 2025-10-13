# NetSuite Integration Hub - Visual Guide

This guide provides a visual walkthrough of the NetSuite Integration Hub interface and user experience.

## 📱 Application Layout

```
┌─────────────────────────────────────────────────────────────┐
│  NetSuite Integration Hub                  [🌙 Dark Mode]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🔄 NetSuite Integration Hub                                 │
│  Connect and sync data from multiple sources to NetSuite     │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  📈 Integration Statistics                                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐               │
│  │  📦    │ │  ✅    │ │  ❌    │ │  🔌    │               │
│  │ Total  │ │Success │ │ Failed │ │ Active │               │
│  │   0    │ │   0    │ │   0    │ │   6    │               │
│  └────────┘ └────────┘ └────────┘ └────────┘               │
│  Last sync: --                                               │
│  [Clear Statistics]                                          │
├─────────────────────────────────────────────────────────────┤
│  📁 Select Data Source                                       │
│  ┌───────┐ ┌───────┐ ┌───────┐                             │
│  │  📄   │ │  🔗   │ │  💾   │                             │
│  │ CSV   │ │ JSON  │ │  DB   │                             │
│  │ File  │ │  API  │ │       │                             │
│  └───────┘ └───────┘ └───────┘                             │
│  ┌───────┐ ┌───────┐ ┌───────┐                             │
│  │  🌐   │ │  ☁️   │ │  🔔   │                             │
│  │ REST  │ │Salesf │ │Webhook│                             │
│  │  API  │ │ force │ │       │                             │
│  └───────┘ └───────┘ └───────┘                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Integration Workflow

### Step 1: Initial State
```
┌─────────────────────────────────────────────┐
│ 📁 Select Data Source                       │
│                                             │
│  Click any source card to begin...         │
│                                             │
│  • CSV File - Import from CSV files        │
│  • JSON API - Connect to JSON endpoints    │
│  • Database - Direct DB connections        │
│  • REST API - Generic API integration      │
│  • Salesforce - CRM connector              │
│  • Webhook - Real-time data receiver       │
└─────────────────────────────────────────────┘
```

### Step 2: Source Selected
```
┌─────────────────────────────────────────────────────┐
│ 🔄 Active Integration: CSV File            [Reset] │
│                                                     │
│ ℹ️  Selected CSV File as data source               │
│                                                     │
│ [1. Connect to Source]                             │
│ [2. Auto-Map Fields]  (disabled)                   │
│ [3. Sync to NetSuite] (disabled)                   │
└─────────────────────────────────────────────────────┘
```

### Step 3: Connecting
```
┌─────────────────────────────────────────────────────┐
│ 🔄 Active Integration: CSV File            [Reset] │
│                                                     │
│ ℹ️  Connecting to CSV File...                      │
│                                                     │
│ Progress                                            │
│ ████████████░░░░░░░░░░░░░░░░░░░░░░░ 60%           │
│                                                     │
│ [1. Connect to Source]                             │
│ [2. Auto-Map Fields]  (disabled)                   │
│ [3. Sync to NetSuite] (disabled)                   │
└─────────────────────────────────────────────────────┘
```

### Step 4: Connected - Data Preview
```
┌─────────────────────────────────────────────────────┐
│ 🔄 Active Integration: CSV File            [Reset] │
│                                                     │
│ ℹ️  Successfully connected! Found 3 records        │
│                                                     │
│ [1. Connect to Source]                             │
│ [2. Auto-Map Fields]                               │
│ [3. Sync to NetSuite]                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 📋 Source Data (3 records)                         │
│                                                     │
│ ┌─────┬─────────────┬──────────────┬──────────┬────┐│
│ │ id  │ name        │ email        │ phone    │loc │
│ ├─────┼─────────────┼──────────────┼──────────┼────┤│
│ │ 1   │ Acme Corp   │contact@acme..│+1-555-...│ NY ││
│ │ 2   │TechStart Inc│info@techst...│+1-555-...│ SF ││
│ │ 3   │Global Sol...│hello@globa...│+1-555-...│Lon ││
│ └─────┴─────────────┴──────────────┴──────────┴────┘│
└─────────────────────────────────────────────────────┘
```

### Step 5: Field Mapping
```
┌─────────────────────────────────────────────────────┐
│ 🔀 Field Mapping                                    │
│                                                     │
│  [id]  →  [Account ID]                             │
│  [name]  →  [Customer Name]                        │
│  [email]  →  [Email]                               │
│  [phone]  →  [Phone]                               │
│  [location]  →  [Address]                          │
│                                                     │
│  ℹ️  Auto-mapped 5 fields                          │
└─────────────────────────────────────────────────────┘
```

### Step 6: Syncing to NetSuite
```
┌─────────────────────────────────────────────────────┐
│ 🔄 Active Integration: CSV File            [Reset] │
│                                                     │
│ ℹ️  Syncing data to NetSuite...                    │
│                                                     │
│ Progress                                            │
│ ████████████████████████████░░░░░░░ 67%           │
│                                                     │
│ [1. Connect to Source]  (disabled)                 │
│ [2. Auto-Map Fields]  (disabled)                   │
│ [3. Sync to NetSuite]  (disabled)                  │
└─────────────────────────────────────────────────────┘
```

### Step 7: Sync Complete
```
┌─────────────────────────────────────────────────────┐
│ ✅ Synced to NetSuite (3 records)                   │
│                                                     │
│ ┌─────────────────────────────────────────────────┐│
│ │ Customer Name: Acme Corp           [Success ✅] ││
│ │ Email: contact@acme.com                         ││
│ │ Phone: +1-555-0101                              ││
│ │ Address: New York                               ││
│ │ Account ID: 1                                   ││
│ └─────────────────────────────────────────────────┘│
│ ┌─────────────────────────────────────────────────┐│
│ │ Customer Name: TechStart Inc       [Success ✅] ││
│ │ Email: info@techstart.com                       ││
│ │ Phone: +1-555-0102                              ││
│ │ Address: San Francisco                          ││
│ │ Account ID: 2                                   ││
│ └─────────────────────────────────────────────────┘│
│ ┌─────────────────────────────────────────────────┐│
│ │ Customer Name: Global Solutions    [Error ❌]   ││
│ │ Email: hello@global.com                         ││
│ │ Validation error: Missing required field        ││
│ └─────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

### Step 8: Integration Logs
```
┌─────────────────────────────────────────────────────┐
│ 📝 Integration Logs                                 │
│                                                     │
│ ┌──────────┬────────┬────────┬────────┬─────────┐ │
│ │Timestamp │Action  │Source  │Status  │Records  │ │
│ ├──────────┼────────┼────────┼────────┼─────────┤ │
│ │12:30:45  │Sync    │CSV File│Complete│    3    │ │
│ │12:30:10  │Connect │CSV File│Success │    3    │ │
│ └──────────┴────────┴────────┴────────┴─────────┘ │
└─────────────────────────────────────────────────────┘
```

## 🎨 Component Showcase

### Statistics Cards
```
┌────────────────┐
│      📦        │
│                │
│ Total Records  │
│      12        │
└────────────────┘
```

### Source Selection Cards
```
┌──────────────────────┐
│         📄           │
│                      │
│      CSV File        │
│                      │
│ Import from CSV files│
│                      │
│  [Select Source]     │
└──────────────────────┘
```
*Hover effect: Card lifts up with shadow*

### Progress Bar
```
Progress: 75%
████████████████████████████░░░░░░░░░░
```

### Status Badges
```
[Success ✅]  [Error ❌]  [Completed]
```

### Field Mapping Visual
```
Source Field     →    NetSuite Field
[company]        →    [Customer Name]
[email]          →    [Email]
[phone]          →    [Phone]
```

## 📊 Data Source Comparison

### CSV File
```
Fields: id, name, email, phone, location
Records: 3
Pattern: Simple, direct field names
```

### JSON API
```
Fields: customer_id, company, contact_email, tel, city
Records: 2
Pattern: Compound names (contact_*, etc.)
```

### Database
```
Fields: cust_id, cust_name, email_address, phone_number, region
Records: 3
Pattern: Prefixes (cust_*, *_number)
```

### REST API
```
Fields: api_id, org_name, primary_email, contact_phone, headquarters
Records: 2
Pattern: Descriptive prefixes (primary_*, contact_*)
```

### Salesforce
```
Fields: sf_id, account_name, email, phone, billing_city
Records: 3
Pattern: Business terms (account_*, billing_*)
```

### Webhook
```
Fields: webhook_id, entity_name, contact_email, phone_num, address
Records: 2
Pattern: Mixed conventions (entity_*, *_num)
```

## 🎯 User Flow Diagram

```
    Start
      ↓
┌─────────────┐
│   Select    │
│   Source    │
└─────────────┘
      ↓
┌─────────────┐     ┌──────────┐
│   Connect   │ →   │ Progress │
│  to Source  │     │   Bar    │
└─────────────┘     └──────────┘
      ↓
┌─────────────┐
│   Preview   │
│  Data Table │
└─────────────┘
      ↓
┌─────────────┐
│  Auto-Map   │
│   Fields    │
└─────────────┘
      ↓
┌─────────────┐     ┌──────────┐
│    Sync     │ →   │ Progress │
│ to NetSuite │     │   Bar    │
└─────────────┘     └──────────┘
      ↓
┌─────────────┐
│   Review    │
│   Results   │
└─────────────┘
      ↓
┌─────────────┐
│ Integration │
│    Logs     │
└─────────────┘
      ↓
    Done
```

## 🌈 Color Scheme

### Light Mode
- Background: White (#FFFFFF)
- Cards: Light Gray (#F9FAFB)
- Primary: Blue (#3B82F6)
- Success: Green (#10B981)
- Error: Red (#EF4444)
- Text: Dark Gray (#1F2937)

### Dark Mode
- Background: Dark (#111111)
- Cards: Dark Gray (#1F2937)
- Primary: Blue (#60A5FA)
- Success: Green (#34D399)
- Error: Red (#F87171)
- Text: Light Gray (#F3F4F6)

## 📏 Responsive Breakpoints

### Desktop (1200px+)
```
┌─────────────────────────────────────┐
│  [Card] [Card] [Card]               │
│  [Card] [Card] [Card]               │
│                                     │
│  [Wide Table View]                  │
└─────────────────────────────────────┘
```

### Tablet (768px - 1199px)
```
┌───────────────────────┐
│  [Card] [Card]        │
│  [Card] [Card]        │
│                       │
│  [Scrollable Table]   │
└───────────────────────┘
```

### Mobile (< 768px)
```
┌─────────────┐
│   [Card]    │
│   [Card]    │
│   [Card]    │
│             │
│  [Stacked]  │
│   [Table]   │
└─────────────┘
```

## 🎬 Animation & Transitions

### Card Hover
```
Before:          After (Hover):
┌──────┐         ┌──────┐
│      │    →    │      │ ↑
│ Card │         │ Card │ (Lifted)
└──────┘         └──────┘
                   Shadow
```

### Progress Bar Animation
```
Frame 1:  ████░░░░░░░░░░░░░░ 20%
Frame 2:  ████████░░░░░░░░░░ 40%
Frame 3:  ████████████░░░░░░ 60%
Frame 4:  ████████████████░░ 80%
Frame 5:  ██████████████████ 100%
```

### Status Badge Transition
```
Loading:  [⟳ Syncing...]
Success:  [✅ Success]
Error:    [❌ Error]
```

## 🖼️ Key Screens

### 1. Landing Screen
- Statistics dashboard (all zeros)
- 6 source selection cards
- Clean, organized layout

### 2. Active Integration Screen
- Selected source highlighted
- Action buttons enabled/disabled dynamically
- Real-time status messages

### 3. Data Preview Screen
- Source data table
- Field mapping visualization
- Action buttons

### 4. Sync Progress Screen
- Progress bar animation
- Status updates
- Loading indicators

### 5. Results Screen
- Synced records with badges
- Success/error counts
- Integration logs

## 🎨 Visual Hierarchy

```
Level 1: Main Heading (size="9")
   🔄 NetSuite Integration Hub

Level 2: Section Headings (size="6")
   📈 Integration Statistics

Level 3: Card Titles (size="5")
   📋 Source Data

Level 4: Labels (size="2")
   Total Records

Level 5: Body Text (size="2")
   Regular content text
```

## 🔔 User Feedback Elements

### Callout Messages
```
┌─────────────────────────────────────┐
│ ℹ️  Successfully connected! Found 3  │
│     records                          │
└─────────────────────────────────────┘
```

### Progress Indicators
```
┌─────────────────────────────────────┐
│ Progress                             │
│ ████████████████████░░░░░░ 65%      │
└─────────────────────────────────────┘
```

### Status Badges
```
[Success ✅]  [Error ❌]  [Completed]
```

### Loading States
```
[⟳ Loading...]
```

## 💻 Terminal Output

### Running the App
```bash
$ ./run.sh
🔄 Starting NetSuite Integration Hub...
🔧 Activating virtual environment...
🌟 Starting Reflex application...
   Open your browser to: http://localhost:3000
   Press Ctrl+C to stop the server

─────────────────────── Starting Reflex App ───────────────────────
[ 12:00:00 ] Compiling:                              100%  21/21
Success: App compiled successfully!
─────────────────────────────────────────────────────────────────────
App running at: http://localhost:3000
```

### Demo Script
```bash
$ python3 demo.py
🔄 NetSuite Integration Hub - Feature Demo
======================================================================

📁 Supported Data Sources:
  • CSV File       📄  - Import customer data from CSV files
  • JSON API       🔗  - Connect to JSON REST endpoints
  ...
```

## 🎯 Tips for Best Experience

1. **Start with CSV** - Easiest source to understand
2. **Watch the Progress** - See real-time updates
3. **Review Field Mapping** - Understand intelligent mapping
4. **Check Integration Logs** - Monitor all activities
5. **Try Different Sources** - See mapping variations
6. **Toggle Dark Mode** - For comfortable viewing

## 🌟 Visual Highlights

- **Emoji Icons** - Intuitive visual cues throughout
- **Color Coding** - Green for success, red for errors
- **Smooth Animations** - Card hovers, progress bars
- **Responsive Tables** - Horizontal scroll on small screens
- **Status Badges** - Clear visual status indicators
- **Progress Bars** - Real-time sync feedback

---

**Ready to see it in action?**
Run `./run.sh` and open http://localhost:3000 in your browser!
