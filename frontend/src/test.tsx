import { Link } from "react-router-dom";

export const Test = () => {
    const title: string = "test";

    return (
        <div className="Test">
            <h1>{title}</h1>
            <Link to='/'>
                戻る
            </Link>
        </div>
    );
}
