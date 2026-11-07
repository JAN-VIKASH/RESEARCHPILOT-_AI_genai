import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content?: string | null;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  if (content === null || content === undefined || content.trim() === '') {
    return (
      <div className="text-slate-500 italic text-sm py-4 text-left">
        No content available.
      </div>
    );
  }

  return (
    <div className="markdown-content text-left">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-[32px] font-bold text-white mt-8 mb-4 leading-tight" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-2xl font-semibold text-white mt-6 mb-3 border-b border-slate-750 pb-2 leading-snug" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-xl font-semibold text-slate-100 mt-5 mb-2 leading-snug" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="text-lg font-semibold text-slate-200 mt-4 mb-2" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="text-slate-350 text-sm leading-relaxed mb-4" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-5 space-y-2 mb-4 text-sm text-slate-300" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-5 space-y-2 mb-4 text-sm text-slate-300" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="text-slate-350 text-sm" {...props} />
          ),
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-brand-500 bg-slate-900 bg-opacity-40 px-4 py-2 my-4 rounded-r-xl italic text-slate-400" {...props} />
          ),
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-6 rounded-xl border border-slate-750">
              <table className="min-w-full divide-y divide-slate-750 text-sm text-left" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-slate-900" {...props} />
          ),
          tbody: ({ node, ...props }) => (
            <tbody className="divide-y divide-slate-800 bg-slate-950 bg-opacity-30" {...props} />
          ),
          tr: ({ node, ...props }) => (
            <tr className="hover:bg-slate-900 bg-opacity-20 transition-colors" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-4 py-3 text-xs font-bold text-slate-350 uppercase tracking-wider border-r border-slate-750 last:border-0" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-4 py-3 text-slate-300 border-r border-slate-800 last:border-0" {...props} />
          ),
          code: ({ node, className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || '');
            const inline = !match;
            if (inline) {
              return (
                <code className="bg-slate-900 text-brand-300 px-1.5 py-0.5 rounded-lg text-xs font-mono border border-slate-850" {...props}>
                  {children}
                </code>
              );
            }
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          pre: ({ node, ...props }) => (
            <pre className="bg-slate-900 border border-slate-750 rounded-xl p-4 my-4 overflow-x-auto text-xs font-mono text-slate-200" {...props} />
          ),
          hr: ({ node, ...props }) => (
            <hr className="border-slate-850 my-6" {...props} />
          ),
          a: ({ node, ...props }) => (
            <a className="text-brand-400 hover:text-brand-300 hover:underline transition-colors cursor-pointer" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
