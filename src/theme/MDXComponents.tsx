import React, {type ComponentProps} from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';
import MDXComponents from '@theme-original/MDXComponents';

function BaseUrlImage({src = '', ...props}: ComponentProps<'img'>) {
  const resolvedSrc = useBaseUrl(src);

  return <img {...props} src={resolvedSrc} />;
}

export default {
  ...MDXComponents,
  img: BaseUrlImage,
};
