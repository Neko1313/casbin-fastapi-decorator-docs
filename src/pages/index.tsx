import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/getting-started/installation">
            Get Started
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            style={{marginLeft: '1rem'}}
            href="https://github.com/Neko1313/casbin-fastapi-decorator">
            GitHub
          </Link>
        </div>
      </div>
    </header>
  );
}

type FeatureItem = {
  title: string;
  description: string;
  badge: string;
};

const features: FeatureItem[] = [
  {
    title: 'Decorator-based',
    badge: '🎯',
    description:
      'Apply authorization directly to routes with a decorator. No middleware, no extra parameters in your function signatures.',
  },
  {
    title: 'Casbin-powered',
    badge: '🔒',
    description:
      'Built on Apache Casbin — supports RBAC, ABAC, and any access control model you define in your policy files.',
  },
  {
    title: 'Three optional extras',
    badge: '🧩',
    description:
      'Extend with JWT authentication, SQLAlchemy database-backed policies, or Casdoor OAuth2 — install only what you need.',
  },
];

function Feature({title, description, badge}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center" style={{fontSize: '3rem', marginBottom: '1rem'}}>
        {badge}
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="Authorization decorator factory for FastAPI based on Casbin">
      <HomepageHeader />
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row" style={{marginTop: '2rem', marginBottom: '2rem'}}>
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
