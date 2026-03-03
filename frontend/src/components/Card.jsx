import { Link } from "react-router-dom";

export default function Card({ title, description, icon: Icon, to, disabled }) {
  const baseStyle =
    "rounded-xl p-6 shadow transition flex flex-col justify-between";

  const enabledStyle =
    "bg-white hover:shadow-lg hover:border-blue-500 border cursor-pointer";

  const disabledStyle =
    "bg-gray-200 text-gray-500 cursor-not-allowed";

  const content = (
    <div className={`${baseStyle} ${disabled ? disabledStyle : enabledStyle}`}>
      <div>
        {Icon && <Icon className="w-8 h-8 mb-4 text-blue-600" />}
        <h3 className="text-lg font-bold mb-2">{title}</h3>
        <p className="text-sm">{description}</p>
      </div>

      {!disabled && (
        <span className="mt-4 text-sm font-medium text-blue-600">
          Acessar →
        </span>
      )}
    </div>
  );

  return disabled ? content : <Link to={to}>{content}</Link>;
}
