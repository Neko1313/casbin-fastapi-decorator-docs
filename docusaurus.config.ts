import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'casbin-fastapi-decorator',
  tagline: 'Authorization decorator factory for FastAPI based on Casbin',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://Neko1313.github.io',
  baseUrl: '/casbin-fastapi-decorator-docs/',

  organizationName: 'Neko1313',
  projectName: 'casbin-fastapi-decorator-docs',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/Neko1313/casbin-fastapi-decorator/tree/main/docs/',
          routeBasePath: 'docs',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'casbin-fastapi-decorator',
      logo: {
        alt: 'Casbin Logo',
        src: 'img/logo.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/Neko1313/casbin-fastapi-decorator',
          label: 'GitHub',
          position: 'right',
        },
        {
          href: 'https://pypi.org/project/casbin-fastapi-decorator/',
          label: 'PyPI',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Getting Started', to: '/docs/getting-started/installation'},
            {label: 'Core', to: '/docs/core/permission-guard'},
            {label: 'API Reference', to: '/docs/api-reference/permission-guard'},
          ],
        },
        {
          title: 'Extras',
          items: [
            {label: 'JWT', to: '/docs/extras/jwt/overview'},
            {label: 'Database', to: '/docs/extras/db/overview'},
            {label: 'Casdoor', to: '/docs/extras/casdoor/overview'},
          ],
        },
        {
          title: 'Links',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/Neko1313/casbin-fastapi-decorator',
            },
            {
              label: 'PyPI',
              href: 'https://pypi.org/project/casbin-fastapi-decorator/',
            },
            {
              label: 'Casbin',
              href: 'https://casbin.org/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} casbin-fastapi-decorator. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'ini', 'toml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
