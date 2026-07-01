import Link from 'next/link';

export default function Home() {
  return (
    <main className="space-y-4">
      <h1 className="text-3xl font-bold">JD 驱动的简历优化与面试准备</h1>
      <p>支持 URL / 粘贴 JD / 岗位画像三种输入。</p>
      <Link className="inline-block rounded bg-black px-4 py-2 text-white" href="/zh/optimize">开始</Link>
    </main>
  );
}
