import { Sidebar } from "@/components/sidebar";

export default function ESILayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen bg-slate-50">
            <Sidebar />
            <main className="flex-1 overflow-y-auto px-8 py-10">
                {children}
            </main>
        </div>
    );
}
