export default function InfoCard({ title, icon: Icon, action, children }) {
  return (
    <div className="bg-white rounded-xl shadow border border-gray-200 p-5 space-y-4">

      {(title || Icon || action) && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {Icon && <Icon className="w-5 h-5 text-blue-600" />}

            {title && (
              <h2 className="text-lg font-bold text-gray-800">
                {title}
              </h2>
            )}
          </div>

          {action}
        </div>
      )}

      {children}
    </div>
  );
}
