import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/concepts',
      ],
    },
    {
      type: 'category',
      label: 'Core',
      items: [
        'core/permission-guard',
        'core/auth-required',
        'core/require-permission',
        'core/access-subject',
      ],
    },
    {
      type: 'category',
      label: 'Extras',
      items: [
        {
          type: 'category',
          label: 'JWT',
          items: [
            'extras/jwt/overview',
            'extras/jwt/bearer-token',
            'extras/jwt/cookie',
          ],
        },
        {
          type: 'category',
          label: 'Database',
          items: [
            'extras/db/overview',
            'extras/db/sqlalchemy-adapter',
          ],
        },
        {
          type: 'category',
          label: 'Casdoor',
          items: [
            'extras/casdoor/overview',
            'extras/casdoor/setup',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Examples',
      items: [
        'examples/basic',
        'examples/with-jwt',
        'examples/with-database',
        'examples/with-casdoor',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api-reference/permission-guard',
        'api-reference/access-subject',
      ],
    },
  ],
};

export default sidebars;
