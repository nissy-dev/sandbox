import { useRef, useState, Fragment, useEffect, useCallback } from "react";
import { Listbox } from "@headlessui/react";

type Option = {
  label: string;
  value: string;
};

const options: Option[] = [...new Array(20)].map((_, i) => ({
  value: `option-${i}`,
  label: `Option ${i}`,
}));

// TODO: インタフェースは後で考える
type Props = {
  options: Option[];
};

const findOptionByValue = (options: Option[], value: string) => {
  return options.find((option) => option.value === value);
};

const Combobox = (props: Props) => {
  const { options } = props;
  const ref = useRef<HTMLInputElement>(null);
  // ポップアップの開閉状態
  const [showListbox, setShowListbox] = useState(false);
  // inputにフォーカスを強制するかどうかを考える
  const [shouldFocusInput, setShouldFocusInput] = useState(false);
  const [inputText, setInputText] = useState("");
  // 選択されている選択肢の状態
  const [selectedOption, setSelectedOption] = useState(options[0]);

  useEffect(() => {
    setInputText(selectedOption.label);

    if (ref.current && ref.current !== null) {
      if (shouldFocusInput) {
        ref.current.focus();
      }
    }
  }, [shouldFocusInput, selectedOption.label]);

  const handleSelectOption = useCallback(
    (value: string) => {
      const option = findOptionByValue(options, value);
      if (option) {
        setSelectedOption(option);
        setInputText(option.label);
      }
    },
    [options]
  );

  return (
    <div>
      {/* @ts-ignore */}
      <Listbox value={selectedOption} onChange={handleSelectOption}>
        <Listbox.Button as={Fragment}>
          <div
            id="combobox-input-div"
            role="combobox"
            aria-expanded={showListbox}
            aria-haspopup={true}
            aria-controls="headlessui-listbox-options-2"
          >
            <input
              ref={ref}
              className="h-10 border border-gray-300 rounded pl-2 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
              type="text"
              value={inputText}
              autoComplete="off"
              aria-activedescendant={undefined}
              aria-autocomplete="list"
              onChange={(event) => {
                setInputText(event.target.value);
              }}
              onClick={() => {
                setShouldFocusInput(true);
              }}
            />
          </div>
        </Listbox.Button>
        <Listbox.Options as={Fragment}>
          <ul className="max-h-80 rounded overflow-y-auto shadow-md focus:outline-none">
            {options.map((option) => (
              <Listbox.Option
                key={option.value}
                value={option.value}
                as={Fragment}
              >
                {({ active, selected }) => (
                  <li
                    className={`pl-4 py-2 ${
                      active && selected ? "bg-blue-100" : ""
                    } ${active && !selected ? "bg-gray-100" : ""}
                    ${!active && selected ? "bg-blue-50" : ""}`}
                  >{`${option.label} ${selected ? "✓" : ""}`}</li>
                )}
              </Listbox.Option>
            ))}
          </ul>
        </Listbox.Options>
      </Listbox>
    </div>
  );
};

export default function App() {
  return (
    <div className="flex flex-col justify-center items-center mt-4">
      <Combobox options={options} />
    </div>
  );
}
