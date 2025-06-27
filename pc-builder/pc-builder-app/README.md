# PC Builder UI

## Overview
PC Builder UI is an Angular application that enables users to build and customize PC configurations. It offers an intuitive interface for selecting components, checking compatibility, and generating a complete build list.

**Note:** All product data and images are served from the backend API, which loads the latest data from AWS S3. The frontend does not require any local assets or CSV files.

## Project Structure

```
pc-builder-app
├── src
│   ├── app
│   │   ├── components/             # Feature and shared components
│   │   ├── services/               # Angular services for data and logic
│   │   ├── models/                 # TypeScript interfaces and models
│   │   ├── app-routing.module.ts   # Application routing configuration
│   │   ├── app.component.ts        # Root component logic
│   │   ├── app.component.html      # Root component template
│   │   ├── app.component.scss      # Root component styles (SCSS)
│   │   └── app.module.ts           # Root module
│   ├── assets/                     # Static assets (images, fonts, etc.)
│   ├── environments/               # Environment-specific settings
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   └── main.ts                     # Application entry point
├── angular.json                    # Angular CLI configuration
├── package.json                    # npm configuration and dependencies
├── tsconfig.json                   # TypeScript configuration
├── .editorconfig                   # Editor configuration
├── .gitignore                      # Git ignore rules
└── README.md                       # Project documentation
```

## Getting Started

### Prerequisites
- Node.js (version 16 or later)
- Angular CLI (install globally: `npm install -g @angular/cli`)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/pc-builder-app.git
   ```
2. Navigate to the project directory:
   ```sh
   cd pc-builder-app
   ```
3. Install dependencies:
   ```sh
   npm install
   ```

### Running the Application
Start the development server:
```sh
ng serve
```
Open your browser at [http://localhost:4200](http://localhost:4200).

### Building for Production
To build the application for production:
```sh
ng build
```
The output will be in the `dist/` directory.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.