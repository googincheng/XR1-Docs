import React, {type ComponentProps} from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';
import MDXComponents from '@theme-original/MDXComponents';

function ManualImage({src = '', ...props}: ComponentProps<'img'>) {
  return <img {...props} src={useBaseUrl(src)} />;
}

export default {
  ...MDXComponents,
  ManualImage,
};
