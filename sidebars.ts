import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';
import fs from 'node:fs';
import path from 'node:path';
import GithubSlugger from 'github-slugger';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const manualDir = path.join(__dirname, 'docs', 'xrecer-xr1');

const chapterFiles = fs
  .readdirSync(manualDir)
  .filter((file) => /^\d{2}-.*\.mdx$/.test(file))
  .sort();

const chapterItems = chapterFiles.map((file) => {
  const source = fs.readFileSync(path.join(manualDir, file), 'utf8');
  const id = `xrecer-xr1/${file.replace(/^\d{2}-/, '').replace(/\.mdx$/, '')}`;
  const title = source.match(/^title:\s*(.+)$/m)?.[1]?.trim() ?? id;
  const route = source.match(/^slug:\s*\/(.+)$/m)?.[1]?.trim();
  const slugger = new GithubSlugger();
  slugger.slug(title);

  const headings = [...source.matchAll(/^##\s+(.+)$/gm)].map((match) => {
    const label = match[1].trim();
    return {
      type: 'link' as const,
      label,
      href: encodeURI(`/docs/${route}#${slugger.slug(label)}`),
    };
  });

  return {
    type: 'category' as const,
    label: title,
    collapsed: true,
    collapsible: true,
    link: {
      type: 'doc' as const,
      id,
    },
    items: headings,
  };
});

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'XRecer XR1',
      collapsed: false,
      collapsible: true,
      link: {
        type: 'doc',
        id: 'xrecer-xr1/intro',
      },
      items: chapterItems,
    },
  ],
};

export default sidebars;
